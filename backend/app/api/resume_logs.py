"""简历修改日志（模块一）。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Resume, ResumeLog
from ..schemas.resume import ResumeLogCreate, ResumeLogOut

router = APIRouter(prefix="/api", tags=["简历修改日志"])


@router.get("/resumes/{resume_id}/logs")
def list_resume_logs(resume_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Resume, resume_id, "简历版本")
    rows = db.scalars(
        select(ResumeLog)
        .where(ResumeLog.resume_version_id == resume_id)
        .order_by(ResumeLog.changed_at.desc(), ResumeLog.id.desc())
    ).all()
    return ok([ResumeLogOut.model_validate(r) for r in rows])


@router.post("/resume-logs")
def create_resume_log(body: ResumeLogCreate, db: Session = Depends(get_db)):
    get_or_404(db, Resume, body.resume_version_id, "简历版本")
    row = ResumeLog(
        resume_version_id=body.resume_version_id,
        change_desc=body.change_desc,
        changed_at=body.changed_at or datetime.now(),
        trigger_source="manual",
    )
    db.add(row)
    db.flush()
    return ok(ResumeLogOut.model_validate(row))