"""题库 CRUD（模块三）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..core.response import ok, page_data
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Question
from ..schemas.exam import (
    QuestionCreate,
    QuestionOut,
    QuestionUpdate,
    ReviewStatusIn,
)

router = APIRouter(prefix="/api/questions", tags=["题库"])


@router.get("")
def list_questions(
    category: str | None = None,
    difficulty: str | None = None,
    review_status: str | None = None,
    keyword: str | None = None,
    tag: str | None = None,
    page: int | None = Query(None, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Question).order_by(Question.updated_at.desc(), Question.id.desc())
    conds = []
    if category:
        conds.append(Question.category == category)
    if difficulty:
        conds.append(Question.difficulty == difficulty)
    if review_status:
        conds.append(Question.review_status == review_status)
    if keyword:
        like = f"%{keyword}%"
        conds.append(
            or_(Question.title.ilike(like), Question.content.ilike(like), Question.source.ilike(like))
        )
    if tag:
        stmt = stmt.where(Question.tags.contains(tag))
    if conds:
        stmt = stmt.where(*conds)

    if page is None:
        rows = db.scalars(stmt).all()
        return ok([QuestionOut.model_validate(r) for r in rows])

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    items = [QuestionOut.model_validate(r) for r in rows]
    return ok(page_data(items, total, page, page_size))


@router.post("")
def create_question(body: QuestionCreate, db: Session = Depends(get_db)):
    data = body.model_dump()
    if not data.get("review_status"):
        data["review_status"] = "new"
    row = Question(**data)
    db.add(row)
    db.flush()
    return ok(QuestionOut.model_validate(row))


@router.put("/{question_id}")
def update_question(question_id: int, body: QuestionUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Question, question_id, "题目")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(QuestionOut.model_validate(row))


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Question, question_id, "题目")
    db.delete(row)
    db.flush()
    return ok(None)


@router.put("/{question_id}/review-status")
def update_question_review_status(
    question_id: int,
    body: ReviewStatusIn,
    db: Session = Depends(get_db),
):
    row = get_or_404(db, Question, question_id, "题目")
    row.review_status = body.review_status
    db.flush()
    return ok(QuestionOut.model_validate(row))