"""面试 CRUD + 问答复盘 + 结果 + 录音上传（模块三）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.errors import AppError
from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Application, Interview, InterviewQa, InterviewResult
from ..schemas.exam import (
    InterviewCreate,
    InterviewOut,
    InterviewQaCreate,
    InterviewQaOut,
    InterviewResultIn,
    InterviewResultOut,
    InterviewUpdate,
)
from ..services.storage import ext_of, queue_file_delete, save_upload

router = APIRouter(prefix="/api/interviews", tags=["面试"])


def _result_of(db: Session, interview_id: int) -> InterviewResult | None:
    return db.scalar(select(InterviewResult).where(InterviewResult.interview_id == interview_id))


@router.get("")
def list_interviews(
    application_id: int | None = None,
    status: str | None = None,
    round: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Interview).order_by(Interview.interview_time.desc().nullslast(), Interview.id.desc())
    conds = []
    if application_id:
        conds.append(Interview.application_id == application_id)
    if status:
        conds.append(Interview.status == status)
    if round:
        conds.append(Interview.round == round)
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([InterviewOut.model_validate(r) for r in rows])


@router.post("")
def create_interview(body: InterviewCreate, db: Session = Depends(get_db)):
    if body.application_id:
        get_or_404(db, Application, body.application_id, "投递记录")
    data = body.model_dump()
    if not data.get("status"):
        data["status"] = "upcoming"
    row = Interview(**data)
    db.add(row)
    db.flush()
    return ok(InterviewOut.model_validate(row))


@router.put("/{interview_id}")
def update_interview(interview_id: int, body: InterviewUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Interview, interview_id, "面试记录")
    data = body.model_dump(exclude_unset=True)
    if data.get("application_id"):
        get_or_404(db, Application, data["application_id"], "投递记录")
    for key, value in data.items():
        setattr(row, key, value)
    db.flush()
    return ok(InterviewOut.model_validate(row))


@router.delete("/{interview_id}")
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Interview, interview_id, "面试记录")
    result = _result_of(db, interview_id)
    if result:
        queue_file_delete(db, result.audio_path)
    db.delete(row)
    db.flush()
    return ok(None)


@router.get("/{interview_id}/qa")
def list_interview_qa(interview_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Interview, interview_id, "面试记录")
    rows = db.scalars(
        select(InterviewQa)
        .where(InterviewQa.interview_id == interview_id)
        .order_by(InterviewQa.created_at, InterviewQa.id)
    ).all()
    return ok([InterviewQaOut.model_validate(r) for r in rows])


@router.post("/{interview_id}/qa")
def create_interview_qa(interview_id: int, body: InterviewQaCreate, db: Session = Depends(get_db)):
    get_or_404(db, Interview, interview_id, "面试记录")
    row = InterviewQa(interview_id=interview_id, **body.model_dump())
    db.add(row)
    db.flush()
    return ok(InterviewQaOut.model_validate(row))


@router.get("/{interview_id}/result")
def get_interview_result(interview_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Interview, interview_id, "面试记录")
    result = _result_of(db, interview_id)
    return ok(InterviewResultOut.model_validate(result).model_dump() if result else None)


@router.put("/{interview_id}/result")
def upsert_interview_result(
    interview_id: int,
    body: InterviewResultIn,
    db: Session = Depends(get_db),
):
    get_or_404(db, Interview, interview_id, "面试记录")
    result = _result_of(db, interview_id)
    data = body.model_dump()
    if result is None:
        result = InterviewResult(interview_id=interview_id, **data)
        db.add(result)
    else:
        for key, value in data.items():
            setattr(result, key, value)
    db.flush()
    return ok(InterviewResultOut.model_validate(result))


@router.post("/{interview_id}/audio")
async def upload_interview_audio(
    interview_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    get_or_404(db, Interview, interview_id, "面试记录")
    ext = ext_of(file.filename or "")
    if ext not in ("mp3", "m4a", "wav"):
        raise AppError(40000, "录音仅支持 mp3 / m4a / wav 格式")
    rel, _size = await save_upload("audios", file, prefix=f"interview{interview_id}")
    result = _result_of(db, interview_id)
    if result is None:
        result = InterviewResult(interview_id=interview_id)
        db.add(result)
    old_audio_path = result.audio_path
    result.audio_path = rel
    if old_audio_path and old_audio_path != rel:
        queue_file_delete(db, old_audio_path)
    db.flush()
    return ok(InterviewResultOut.model_validate(result))
