"""黑名单/避雷库 CRUD（模块五）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Blacklist
from ..schemas.misc import BlacklistCreate, BlacklistOut, BlacklistUpdate

router = APIRouter(prefix="/api/blacklist", tags=["黑名单"])


@router.get("/check")
def check_blacklist(company: str, db: Session = Depends(get_db)):
    """投递录入时调用：查询某公司命中条数。"""
    count = db.scalar(
        select(func.count(Blacklist.id)).where(Blacklist.company == company)
    ) or 0
    return ok({"company": company, "count": count})


@router.get("")
def list_blacklist(
    company: str | None = None,
    issue_type: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Blacklist).order_by(Blacklist.updated_at.desc(), Blacklist.id.desc())
    conds = []
    if company:
        conds.append(Blacklist.company.ilike(f"%{company}%"))
    if issue_type:
        conds.append(Blacklist.issue_type == issue_type)
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([BlacklistOut.model_validate(r) for r in rows])


@router.post("")
def create_blacklist(body: BlacklistCreate, db: Session = Depends(get_db)):
    row = Blacklist(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(BlacklistOut.model_validate(row))


@router.put("/{blacklist_id}")
def update_blacklist(blacklist_id: int, body: BlacklistUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Blacklist, blacklist_id, "黑名单记录")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(BlacklistOut.model_validate(row))


@router.delete("/{blacklist_id}")
def delete_blacklist(blacklist_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Blacklist, blacklist_id, "黑名单记录")
    db.delete(row)
    db.flush()
    return ok(None)