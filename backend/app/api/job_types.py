"""岗位类型 CRUD（模块一）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.errors import AppError
from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import JobType, Resume
from ..schemas.resume import JobTypeCreate, JobTypeOut, JobTypeUpdate

router = APIRouter(prefix="/api/job-types", tags=["岗位类型"])


@router.get("")
def list_job_types(db: Session = Depends(get_db)):
    rows = db.scalars(select(JobType).order_by(JobType.sort_order, JobType.id)).all()
    return ok([JobTypeOut.model_validate(r) for r in rows])


@router.post("")
def create_job_type(body: JobTypeCreate, db: Session = Depends(get_db)):
    dup = db.scalar(select(JobType.id).where(JobType.name == body.name))
    if dup:
        raise AppError(40900, f"岗位类型「{body.name}」已存在", 409)
    row = JobType(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(JobTypeOut.model_validate(row))


@router.put("/{job_type_id}")
def update_job_type(job_type_id: int, body: JobTypeUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, JobType, job_type_id, "岗位类型")
    data = body.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        dup = db.scalar(select(JobType.id).where(JobType.name == data["name"], JobType.id != job_type_id))
        if dup:
            raise AppError(40900, f"岗位类型「{data['name']}」已存在", 409)
    for key, value in data.items():
        setattr(row, key, value)
    db.flush()
    return ok(JobTypeOut.model_validate(row))


@router.delete("/{job_type_id}")
def delete_job_type(job_type_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, JobType, job_type_id, "岗位类型")
    count = db.scalar(select(func.count(Resume.id)).where(Resume.job_type_id == job_type_id)) or 0
    if count:
        raise AppError(
            40900, f"该岗位类型下仍有 {count} 份简历版本，请先迁移或删除关联简历后再删除", 409
        )
    db.delete(row)
    db.flush()
    return ok(None)