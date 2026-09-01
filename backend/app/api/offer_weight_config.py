"""Offer 打分权重配置（模块二）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.errors import AppError
from ..core.response import ok
from ..database import get_db
from ..models import OfferWeightConfig
from ..schemas.application import OfferWeightIn, OfferWeightOut

router = APIRouter(prefix="/api/offer-weight-config", tags=["Offer 权重配置"])


@router.get("")
def get_weight_config(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(OfferWeightConfig).order_by(OfferWeightConfig.sort_order, OfferWeightConfig.id)
    ).all()
    return ok([OfferWeightOut.model_validate(r) for r in rows])


@router.put("")
def update_weight_config(body: list[OfferWeightIn], db: Session = Depends(get_db)):
    keys = [item.dimension_key for item in body]
    if len(keys) != len(set(keys)):
        raise AppError(40000, "权重配置中存在重复的维度 key")
    # 整体覆盖：先清空再写入
    db.query(OfferWeightConfig).delete()
    for idx, item in enumerate(body):
        db.add(
            OfferWeightConfig(
                dimension_key=item.dimension_key,
                dimension_name=item.dimension_name,
                weight=item.weight,
                enabled=item.enabled,
                sort_order=item.sort_order,
            )
        )
    db.flush()
    rows = db.scalars(
        select(OfferWeightConfig).order_by(OfferWeightConfig.sort_order, OfferWeightConfig.id)
    ).all()
    return ok([OfferWeightOut.model_validate(r) for r in rows])