"""Offer 打分与对比服务。

算法（《技术架构与设计》4.2）：
- 每维度得分 D_i ∈ [0,100]，权重 W_i（可配置，默认等权）
- 总分 = Σ(D_i × W_i) / Σ(W_i)（仅对能算出得分的维度归一化）
- 薪资维度：年薪按理想区间线性映射到 [0,100]
- 加班强度：反向映射（越大越卷，得分越低）
"""
from __future__ import annotations

import re

from sqlalchemy.orm import Session

from ..models import Offer, OfferWeightConfig

DEFAULT_IDEAL_RANGE = [240.0, 800.0]  # 年薪区间（单位 K）


def load_weights(configs: list[OfferWeightConfig], overrides: dict | None) -> dict[str, tuple[str, float]]:
    """合并数据库权重与本次对比的临时覆盖，返回 {dimension_key: (名称, 权重)}。"""
    out: dict[str, tuple[str, float]] = {}
    overrides = overrides or {}
    for c in configs:
        if not c.enabled:
            continue
        weight = float(c.weight)
        ov = overrides.get(c.dimension_key)
        if ov is not None:
            if isinstance(ov, dict):
                if ov.get("enabled") is False:
                    continue
                if "weight" in ov:
                    weight = float(ov["weight"])
            else:
                weight = float(ov)
        if weight > 0:
            out[c.dimension_key] = (c.dimension_name, weight)
    return out


def _company_scale_score(text: str) -> float:
    """公司规模为文本（如 500-1000 人 / 上市公司），粗粒度映射 1-5。"""
    if "上市" in text:
        return 5.0
    nums = re.findall(r"\d[\d,]*", text)
    if nums:
        v = max(int(n.replace(",", "")) for n in nums)
        if v >= 10000:
            return 5.0
        if v >= 1000:
            return 4.0
        if v >= 100:
            return 3.0
        return 2.0
    return 3.0


def dimension_scores(offer: Offer, settings_map: dict) -> dict[str, float]:
    """计算单个 Offer 的各维度原始得分（0-100）。"""
    scores: dict[str, float] = {}

    # 薪资：年薪 = base × 月数 + 绩效奖金 + 签字费（单位 K）
    if offer.salary_base is not None:
        annual = float(offer.salary_base) * (offer.salary_months or 12)
        annual += float(offer.bonus_performance or 0)
        annual += float(offer.signing_bonus or 0)
        ideal = settings_map.get("salary_ideal_range") or DEFAULT_IDEAL_RANGE
        lo, hi = float(ideal[0]), float(ideal[1])
        if hi > lo:
            s = (annual - lo) / (hi - lo) * 100
            scores["salary"] = max(0.0, min(100.0, s))

    # 城市偏好
    if offer.city:
        preferred = settings_map.get("preferred_cities") or []
        scores["city"] = 100.0 if (not preferred or offer.city in preferred) else 60.0

    # 1-5 主观分维度
    if offer.industry_prospect is not None:
        scores["industry"] = float(offer.industry_prospect) * 20
    if offer.position_development is not None:
        scores["position_dev"] = float(offer.position_development) * 20
    if offer.work_intensity is not None:
        scores["work_intensity"] = (6 - float(offer.work_intensity)) * 20  # 反向

    if offer.company_scale:
        scores["company_scale"] = _company_scale_score(offer.company_scale) * 20

    # 自定义维度（extra_scores 中 dimension_key -> 0-100）
    for key, value in (offer.extra_scores or {}).items():
        if isinstance(value, (int, float)):
            scores.setdefault(str(key), float(value))

    return scores


def compare(
    db: Session,
    offers: list[Offer],
    configs: list[OfferWeightConfig],
    overrides: dict | None,
    settings_map: dict,
) -> dict:
    weights = load_weights(configs, overrides)
    results: list[dict] = []
    for offer in offers:
        scores = dimension_scores(offer, settings_map)
        acc = 0.0
        total_w = 0.0
        used: list[str] = []
        for key, (_name, weight) in weights.items():
            if key in scores:
                acc += scores[key] * weight
                total_w += weight
                used.append(key)
        total = round(acc / total_w, 1) if total_w > 0 else 0.0
        results.append(
            {
                "offer_id": offer.id,
                "company": offer.company,
                "position": offer.position,
                "city": offer.city,
                "scores": {key: round(scores[key], 1) for key in used},
                "total": total,
                "recommended": False,
                "rank": 0,
            }
        )

    results.sort(key=lambda r: (r["total"], r["offer_id"]), reverse=True)
    for idx, item in enumerate(results, start=1):
        item["rank"] = idx
    if results:
        results[0]["recommended"] = True

    dimensions = [
        {
            "key": c.dimension_key,
            "name": c.dimension_name,
            "weight": c.weight,
            "enabled": c.enabled,
        }
        for c in sorted(configs, key=lambda c: (c.sort_order, c.id))
    ]
    return {"results": results, "dimensions": dimensions}