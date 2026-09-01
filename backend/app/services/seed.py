"""种子数据：预置岗位类型 / Offer 权重 / 话术模板 / 默认设置（幂等）。"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..core.constants import OFFER_DIMENSIONS
from ..models import JobType, OfferWeightConfig, Script, Setting

DEFAULT_JOB_TYPES = [
    ("算法岗", "#409EFF", 1),
    ("开发岗", "#67C23A", 2),
    ("测试岗", "#E6A23C", 3),
    ("产品岗", "#F56C6C", 4),
]

DEFAULT_SCRIPTS = [
    {
        "category": "general",
        "title": "自我介绍模板",
        "content": "面试官好，我是XXX，XX年毕业，主攻XX方向。\n1. 教育背景：XX大学 XX专业（硕士/本科）\n2. 项目经历：做过XX项目，核心贡献是XX，量化成果XX\n3. 实习经历：在XX公司实习，负责XX\n4. 为什么适合：技能栈匹配 + 主动性 + 学习能力",
    },
    {
        "category": "general",
        "title": "优缺点回答模板",
        "content": "优点：技术基础扎实、自驱力强、做事有闭环（配案例）。\n缺点：避免致命硬伤，讲一个非核心缺点 + 已采取的改进措施。",
    },
    {
        "category": "general",
        "title": "职业规划模板",
        "content": "短期（1-2年）：夯实业务与技术栈，独立负责模块；\n中期（3-5年）：成长为技术骨干/带小团队，深耕XX方向；\n长期：与公司业务共同成长。注意与岗位方向对齐。",
    },
    {
        "category": "general",
        "title": "为什么选择我们公司",
        "content": "1. 业务前景：看好公司所处赛道与产品；\n2. 技术氛围：与我的技术方向/学习方向匹配；\n3. 岗位契合：职责与我过往经历高度相关；\n4. 价值观认同：XX。",
    },
]


def ensure_seed(db: Session) -> None:
    if db.query(JobType).count() == 0:
        for name, color, sort_order in DEFAULT_JOB_TYPES:
            db.add(JobType(name=name, color=color, sort_order=sort_order))

    if db.query(OfferWeightConfig).count() == 0:
        n = len(OFFER_DIMENSIONS)
        for idx, (key, name) in enumerate(OFFER_DIMENSIONS):
            db.add(
                OfferWeightConfig(
                    dimension_key=key,
                    dimension_name=name,
                    weight=round(1.0 / n, 4),
                    enabled=True,
                    sort_order=idx,
                )
            )

    if db.query(Script).count() == 0:
        for script in DEFAULT_SCRIPTS:
            db.add(Script(**script))

    if db.get(Setting, "salary_ideal_range") is None:
        db.add(Setting(key="salary_ideal_range", value="[240, 800]"))
    if db.get(Setting, "preferred_cities") is None:
        db.add(Setting(key="preferred_cities", value="[]"))

    db.commit()


if __name__ == "__main__":  # python -m app.seed
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        ensure_seed(db)
        print("种子数据写入完成")
    finally:
        db.close()