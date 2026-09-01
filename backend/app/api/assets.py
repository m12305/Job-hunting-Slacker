"""资产归档 CRUD + 文件上传（模块一）。"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..config import settings
from ..core.errors import AppError
from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Asset
from ..schemas.resume import AssetCreate, AssetOut, AssetUpdate
from ..services.storage import queue_file_delete, save_upload

router = APIRouter(prefix="/api/assets", tags=["资产归档"])


@router.get("")
def list_assets(
    category: str | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Asset).order_by(Asset.updated_at.desc(), Asset.id.desc())
    conds = []
    if category:
        conds.append(Asset.category == category)
    if keyword:
        like = f"%{keyword}%"
        conds.append(or_(Asset.title.ilike(like), Asset.description.ilike(like)))
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([AssetOut.model_validate(r) for r in rows])


@router.post("")
def create_asset(body: AssetCreate, db: Session = Depends(get_db)):
    if not body.url and not body.file_path:
        raise AppError(40000, "链接类资产需提供 url，文件类资产需提供 file_path")
    row = Asset(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(AssetOut.model_validate(row))


@router.post("/upload")
async def upload_asset(
    category: str = Form(...),
    title: str = Form(...),
    description: str | None = Form(None),
    tags: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    rel, _size = await save_upload(category, file)
    tag_list = None
    if tags:
        try:
            tag_list = json.loads(tags) if isinstance(json.loads(tags), list) else [tags]
        except json.JSONDecodeError:
            tag_list = [tags]
    row = Asset(category=category, title=title, description=description, file_path=rel, tags=tag_list)
    db.add(row)
    db.flush()
    return ok(AssetOut.model_validate(row))


@router.put("/{asset_id}")
def update_asset(asset_id: int, body: AssetUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Asset, asset_id, "资产")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(AssetOut.model_validate(row))


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Asset, asset_id, "资产")
    if settings.file_delete_on_remove:
        queue_file_delete(db, row.file_path)
    db.delete(row)
    db.flush()
    return ok(None)
