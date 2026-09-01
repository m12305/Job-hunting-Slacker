"""简历版本 CRUD / 上传 / 下载 / 预览 / 设默认（模块一）。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..core.errors import AppError
from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import JobType, Resume, ResumeLog
from ..schemas.resume import ResumeCreate, ResumeLogOut, ResumeOut, ResumeUpdate
from ..services.storage import (
    abs_of,
    convert_to_pdf,
    ext_of,
    media_type,
    preview_cache_path,
    rel_of,
    save_upload,
    queue_file_delete,
)
from ..config import settings

router = APIRouter(prefix="/api/resumes", tags=["简历版本"])


def _to_out(resume: Resume, db: Session) -> ResumeOut:
    out = ResumeOut.model_validate(resume)
    if resume.job_type_id:
        jt = db.get(JobType, resume.job_type_id)
        out.job_type_name = jt.name if jt else None
    return out


@router.get("")
def list_resumes(
    job_type_id: int | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(Resume, JobType.name)
        .outerjoin(JobType, Resume.job_type_id == JobType.id)
        .order_by(Resume.updated_at.desc(), Resume.id.desc())
    )
    conds = []
    if job_type_id:
        conds.append(Resume.job_type_id == job_type_id)
    if keyword:
        like = f"%{keyword}%"
        conds.append(
            or_(
                Resume.version_name.ilike(like),
                Resume.target_position.ilike(like),
                Resume.remark.ilike(like),
            )
        )
    if conds:
        stmt = stmt.where(*conds)
    rows = db.execute(stmt).all()
    items = []
    for resume, job_type_name in rows:
        out = ResumeOut.model_validate(resume)
        out.job_type_name = job_type_name
        items.append(out)
    return ok(items)


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    logs = db.scalars(
        select(ResumeLog)
        .where(ResumeLog.resume_version_id == resume_id)
        .order_by(ResumeLog.changed_at.desc(), ResumeLog.id.desc())
    ).all()
    data = _to_out(resume, db).model_dump()
    data["logs"] = [ResumeLogOut.model_validate(x).model_dump() for x in logs]
    return ok(data)


@router.post("")
def create_resume(body: ResumeCreate, db: Session = Depends(get_db)):
    if body.job_type_id:
        get_or_404(db, JobType, body.job_type_id, "岗位类型")
    data = body.model_dump()
    if not data.get("status"):
        data["status"] = "active"
    if data.get("is_default") and data.get("job_type_id"):
        for r in db.scalars(
            select(Resume).where(Resume.job_type_id == data["job_type_id"])
        ).all():
            r.is_default = False
    row = Resume(**data)
    db.add(row)
    db.flush()
    return ok(_to_out(row, db))


@router.put("/{resume_id}")
def update_resume(resume_id: int, body: ResumeUpdate, db: Session = Depends(get_db)):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    data = body.model_dump(exclude_unset=True)
    if data.get("job_type_id"):
        get_or_404(db, JobType, data["job_type_id"], "岗位类型")
    if data.get("is_default") and (data.get("job_type_id") or resume.job_type_id):
        target_type = data.get("job_type_id") or resume.job_type_id
        for r in db.scalars(select(Resume).where(Resume.job_type_id == target_type)).all():
            if r.id != resume_id:
                r.is_default = False
    for key, value in data.items():
        setattr(resume, key, value)
    db.flush()
    return ok(_to_out(resume, db))


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    if settings.file_delete_on_remove:
        queue_file_delete(db, resume.file_path)
        cache_file = preview_cache_path(resume_id)
        queue_file_delete(db, rel_of(cache_file) if cache_file.is_file() else None)
    db.delete(resume)
    db.flush()
    return ok(None)


@router.post("/{resume_id}/upload")
async def upload_resume_file(
    resume_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    ext = ext_of(file.filename or "")
    if ext not in ("pdf", "doc", "docx"):
        raise AppError(40000, "简历仅支持 pdf / doc / docx 文件")
    old_file_path = resume.file_path
    rel, size = await save_upload("resumes", file, prefix=f"resume{resume_id}")
    resume.file_path = rel
    resume.file_name = file.filename
    resume.file_type = ext
    resume.file_size = size
    db.flush()
    db.add(
        ResumeLog(
            resume_version_id=resume_id,
            change_desc=f"上传文件：{file.filename}",
            changed_at=datetime.now(),
        )
    )
    if settings.file_delete_on_remove and old_file_path and old_file_path != rel:
        queue_file_delete(db, old_file_path)
    cache_file = preview_cache_path(resume_id)
    if cache_file.is_file():
        queue_file_delete(db, rel_of(cache_file))
    return ok(_to_out(resume, db))


@router.post("/{resume_id}/set-default")
def set_default_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    if not resume.job_type_id:
        raise AppError(40000, "该简历未关联岗位类型，无法设为默认版本")
    for r in db.scalars(select(Resume).where(Resume.job_type_id == resume.job_type_id)).all():
        r.is_default = r.id == resume_id
    db.flush()
    return ok(_to_out(resume, db))


@router.get("/{resume_id}/file")
def get_resume_file(
    resume_id: int,
    disposition: str = Query("inline", pattern="^(inline|attachment)$"),
    db: Session = Depends(get_db),
):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    if not resume.file_path:
        raise AppError(40400, "该简历尚未上传文件", 404)
    path = abs_of(resume.file_path)
    if not path.is_file():
        raise AppError(40400, "简历文件不存在或已被删除", 404)
    return FileResponse(
        path,
        media_type=media_type(resume.file_type),
        filename=resume.file_name or path.name,
        content_disposition_type=disposition,
    )


@router.get("/{resume_id}/preview")
def preview_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = get_or_404(db, Resume, resume_id, "简历版本")
    if not resume.file_path:
        raise AppError(40400, "该简历尚未上传文件，无法预览", 404)
    path = abs_of(resume.file_path)
    if not path.is_file():
        raise AppError(40400, "简历文件不存在或已被删除", 404)

    if resume.file_type == "pdf":
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=resume.file_name or path.name,
            content_disposition_type="inline",
        )

    if resume.file_type in ("doc", "docx"):
        cache_file = preview_cache_path(resume_id)
        stale = not cache_file.is_file() or path.stat().st_mtime > cache_file.stat().st_mtime
        if stale:
            converted = convert_to_pdf(path, cache_file.parent)
            if converted is None:
                raise AppError(
                    40000,
                    "当前环境不支持 Word 在线预览（缺少 LibreOffice），请改用「下载」查看",
                    409,
                )
            if converted != cache_file:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                converted.replace(cache_file)
        if cache_file.is_file():
            return FileResponse(
                cache_file,
                media_type="application/pdf",
                filename=f"resume_{resume_id}.pdf",
                content_disposition_type="inline",
            )
        raise AppError(50000, "预览文件生成失败")

    raise AppError(40000, "不支持预览该文件格式")
