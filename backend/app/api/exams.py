"""笔试 CRUD + 复盘（模块三）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Application, Exam, ExamReview
from ..schemas.exam import ExamCreate, ExamOut, ExamReviewIn, ExamReviewOut, ExamUpdate

router = APIRouter(prefix="/api/exams", tags=["笔试"])


def _review_of(db: Session, exam_id: int) -> ExamReview | None:
    return db.scalar(select(ExamReview).where(ExamReview.exam_id == exam_id))


@router.get("")
def list_exams(
    application_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Exam).order_by(Exam.exam_time.desc().nullslast(), Exam.id.desc())
    conds = []
    if application_id:
        conds.append(Exam.application_id == application_id)
    if status:
        conds.append(Exam.status == status)
    if conds:
        stmt = stmt.where(*conds)
    rows = db.scalars(stmt).all()
    return ok([ExamOut.model_validate(r) for r in rows])


@router.post("")
def create_exam(body: ExamCreate, db: Session = Depends(get_db)):
    if body.application_id:
        get_or_404(db, Application, body.application_id, "投递记录")
    data = body.model_dump()
    if not data.get("status"):
        data["status"] = "upcoming"
    row = Exam(**data)
    db.add(row)
    db.flush()
    return ok(ExamOut.model_validate(row))


@router.put("/{exam_id}")
def update_exam(exam_id: int, body: ExamUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Exam, exam_id, "笔试记录")
    data = body.model_dump(exclude_unset=True)
    if data.get("application_id"):
        get_or_404(db, Application, data["application_id"], "投递记录")
    for key, value in data.items():
        setattr(row, key, value)
    db.flush()
    return ok(ExamOut.model_validate(row))


@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Exam, exam_id, "笔试记录")
    db.delete(row)
    db.flush()
    return ok(None)


@router.get("/{exam_id}/review")
def get_exam_review(exam_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Exam, exam_id, "笔试记录")
    review = _review_of(db, exam_id)
    return ok(ExamReviewOut.model_validate(review).model_dump() if review else None)


@router.put("/{exam_id}/review")
def upsert_exam_review(exam_id: int, body: ExamReviewIn, db: Session = Depends(get_db)):
    get_or_404(db, Exam, exam_id, "笔试记录")
    review = _review_of(db, exam_id)
    data = body.model_dump(exclude_unset=True)
    if review is None:
        review = ExamReview(exam_id=exam_id, **data)
        db.add(review)
    else:
        for key, value in data.items():
            setattr(review, key, value)
    db.flush()
    return ok(ExamReviewOut.model_validate(review))