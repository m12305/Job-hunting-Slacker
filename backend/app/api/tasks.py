"""每日任务 CRUD + 打卡（模块五）。"""
from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..crud.base import get_or_404
from ..database import get_db
from ..models import Task
from ..schemas.misc import TaskCreate, TaskDoneIn, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["每日任务"])


@router.get("")
def list_tasks(
    due_date: date | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Task).order_by(Task.due_date, Task.id)
    if due_date:
        stmt = stmt.where(Task.due_date == due_date)
    rows = db.scalars(stmt).all()
    return ok([TaskOut.model_validate(r) for r in rows])


@router.post("")
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    row = Task(**body.model_dump())
    db.add(row)
    db.flush()
    return ok(TaskOut.model_validate(row))


@router.put("/{task_id}")
def update_task(task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Task, task_id, "任务")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.flush()
    return ok(TaskOut.model_validate(row))


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Task, task_id, "任务")
    db.delete(row)
    db.flush()
    return ok(None)


@router.put("/{task_id}/done")
def set_task_done(task_id: int, body: TaskDoneIn, db: Session = Depends(get_db)):
    row = get_or_404(db, Task, task_id, "任务")
    row.done = body.done
    row.done_at = datetime.now() if body.done else None
    db.flush()
    return ok(TaskOut.model_validate(row))