"""话术库 CRUD（模块五）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Script
from ..schemas.misc import FavoriteIn, ScriptCreate, ScriptOut, ScriptUpdate

router = APIRouter(prefix="/api/scripts", tags=["话术库"])


@router.get("")
def list_scripts(
    category: str | None = None,
    keyword: str | None = None,
    favorite: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Script).order_by(Script.updated_at.desc(), Script.id.desc())
    conds = []
    if category:
        conds.append(Script.category == category)
    if keyword:
        like = f"%{keyword}%"
        conds.append(or_(Script.title.ilike(like), Script.content.ilike(like)))
    if favorite == 1:
        conds.append(Script.is_favorite.is_(True))
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([ScriptOut.model_validate(r) for r in rows])


@router.post("")
def create_script(body: ScriptCreate, db: Session = Depends(get_db)):
    row = Script(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(ScriptOut.model_validate(row))


@router.put("/{script_id}")
def update_script(script_id: int, body: ScriptUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Script, script_id, "话术")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(ScriptOut.model_validate(row))


@router.delete("/{script_id}")
def delete_script(script_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Script, script_id, "话术")
    db.delete(row)
    db.flush()
    return ok(None)


@router.put("/{script_id}/favorite")
def toggle_favorite(script_id: int, body: FavoriteIn, db: Session = Depends(get_db)):
    row = get_or_404(db, Script, script_id, "话术")
    row.is_favorite = body.favorite
    db.flush()
    return ok(ScriptOut.model_validate(row))


@router.post("/{script_id}/use")
def use_script(script_id: int, db: Session = Depends(get_db)):
    """标记一次使用（复制/引用话术时调用），累计 usage_count。"""
    row = get_or_404(db, Script, script_id, "话术")
    row.usage_count = (row.usage_count or 0) + 1
    db.flush()
    return ok(ScriptOut.model_validate(row))