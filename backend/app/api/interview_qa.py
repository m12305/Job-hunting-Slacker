"""面试问答条目维护（模块三）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import InterviewQa
from ..schemas.exam import InterviewQaOut, InterviewQaUpdate

router = APIRouter(prefix="/api/interview-qa", tags=["面试问答"])


@router.put("/{qa_id}")
def update_interview_qa(qa_id: int, body: InterviewQaUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, InterviewQa, qa_id, "面试问答")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(InterviewQaOut.model_validate(row))


@router.delete("/{qa_id}")
def delete_interview_qa(qa_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, InterviewQa, qa_id, "面试问答")
    db.delete(row)
    db.flush()
    return ok(None)