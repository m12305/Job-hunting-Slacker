"""Offer CRUD + 对比（模块二）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Application, Offer, OfferWeightConfig
from ..schemas.application import OfferCompareIn, OfferCreate, OfferOut, OfferUpdate
from ..services.offer_service import compare
from ..services.settings_service import get_settings_map

router = APIRouter(prefix="/api/offers", tags=["Offer"])


@router.get("")
def list_offers(
    status: str | None = None,
    application_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Offer).order_by(Offer.updated_at.desc(), Offer.id.desc())
    conds = []
    if status:
        conds.append(Offer.status == status)
    if application_id:
        conds.append(Offer.application_id == application_id)
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([OfferOut.model_validate(r) for r in rows])


@router.post("")
def create_offer(body: OfferCreate, db: Session = Depends(get_db)):
    if body.application_id:
        get_or_404(db, Application, body.application_id, "投递记录")
    data = body.model_dump()
    if not data.get("status"):
        data["status"] = "pending"
    row = Offer(**data)
    db.add(row)
    db.flush()
    return ok(OfferOut.model_validate(row))


@router.post("/compare")
def compare_offers(body: OfferCompareIn, db: Session = Depends(get_db)):
    offers = []
    for offer_id in body.offer_ids:
        offers.append(get_or_404(db, Offer, offer_id, "Offer"))
    configs = db.scalars(select(OfferWeightConfig).order_by(OfferWeightConfig.sort_order)).all()
    settings_map = get_settings_map(db)
    return ok(compare(db, offers, configs, body.weight_overrides, settings_map))


@router.get("/{offer_id}")
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Offer, offer_id, "Offer")
    return ok(OfferOut.model_validate(row))


@router.put("/{offer_id}")
def update_offer(offer_id: int, body: OfferUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Offer, offer_id, "Offer")
    data = body.model_dump(exclude_unset=True)
    if data.get("application_id"):
        get_or_404(db, Application, data["application_id"], "投递记录")
    for key, value in data.items():
        setattr(row, key, value)
    db.flush()
    return ok(OfferOut.model_validate(row))


@router.delete("/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Offer, offer_id, "Offer")
    db.delete(row)
    db.flush()
    return ok(None)