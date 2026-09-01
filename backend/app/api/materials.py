"""素材库 CRUD（模块一）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..core.constants import MATERIAL_CATEGORIES
from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Material
from ..schemas.resume import MaterialCreate, MaterialOut, MaterialUpdate

router = APIRouter(prefix="/api/materials", tags=["素材库"])


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    used = db.scalars(select(Material.category).distinct()).all()
    merged = list(MATERIAL_CATEGORIES)
    for c in used:
        if c not in merged:
            merged.append(c)
    return ok(merged)


@router.get("")
def list_materials(
    category: str | None = None,
    keyword: str | None = None,
    tag: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Material).order_by(Material.updated_at.desc(), Material.id.desc())
    conds = []
    if category:
        conds.append(Material.category == category)
    if keyword:
        like = f"%{keyword}%"
        conds.append(
            or_(
                Material.title.ilike(like),
                Material.organization.ilike(like),
                Material.description.ilike(like),
                Material.highlights.ilike(like),
            )
        )
    if tag:
        stmt = stmt.where(Material.tags.contains(tag))
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([MaterialOut.model_validate(r) for r in rows])


@router.post("")
def create_material(body: MaterialCreate, db: Session = Depends(get_db)):
    row = Material(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(MaterialOut.model_validate(row))


@router.put("/{material_id}")
def update_material(material_id: int, body: MaterialUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Material, material_id, "素材")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(MaterialOut.model_validate(row))


@router.delete("/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Material, material_id, "素材")
    db.delete(row)
    db.flush()
    return ok(None)