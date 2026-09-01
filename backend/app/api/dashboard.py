"""每日看板：今日聚合 + 连续打卡（模块五）。"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.response import ok
from ..database import get_db
from ..models import Application, Exam, ExamReview, Interview, InterviewResult, Question, Task
from ..schemas.misc import TaskOut

router = APIRouter(prefix="/api/dashboard", tags=["每日看板"])


def _streak_stats(db: Session, today: date) -> tuple[int, int, int]:
    done_rows = db.scalars(
        select(Task).where(Task.done.is_(True), Task.done_at.is_not(None))
    ).all()
    done_dates = {row.done_at.date() for row in done_rows if row.done_at}

    streak = 0
    day = today if today in done_dates else today - timedelta(days=1)
    while day in done_dates:
        streak += 1
        day -= timedelta(days=1)

    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_tasks = db.scalars(
        select(Task).where(Task.due_date >= monday, Task.due_date <= sunday)
    ).all()
    week_total = len(week_tasks)
    week_done = sum(1 for t in week_tasks if t.done)
    return streak, week_done, week_total


@router.get("/today")
def dashboard_today(db: Session = Depends(get_db)):
    today = date.today()

    # 待投递：投递记录中仍是 pending 的
    pending_apps = db.scalars(
        select(Application).where(Application.status == "pending").order_by(Application.updated_at.desc())
    ).all()

    # 待复盘：已结束笔试未写复盘、已结束面试未记录结果
    reviewed_exam_ids = set(db.scalars(select(ExamReview.exam_id)))
    exams_done = db.scalars(select(Exam).where(Exam.status == "done")).all()
    resulted_interview_ids = set(db.scalars(select(InterviewResult.interview_id)))
    interviews_done = db.scalars(select(Interview).where(Interview.status == "done")).all()

    review_todo = [
        {
            "type": "exam",
            "id": e.id,
            "title": f"笔试复盘 · {e.platform or '平台未填'}",
            "application_id": e.application_id,
        }
        for e in exams_done
        if e.id not in reviewed_exam_ids
    ]
    review_todo += [
        {
            "type": "interview",
            "id": i.id,
            "title": f"面试复盘 · {i.round or '轮次未填'}",
            "application_id": i.application_id,
        }
        for i in interviews_done
        if i.id not in resulted_interview_ids
    ]

    # 待刷题：new/todo 状态的题库
    questions = db.scalars(
        select(Question)
        .where(Question.review_status.in_(["new", "todo"]))
        .order_by(Question.updated_at.desc())
        .limit(100)
    ).all()
    question_todo = [
        {"id": q.id, "title": q.title, "category": q.category, "difficulty": q.difficulty}
        for q in questions
    ]

    tasks_today = db.scalars(select(Task).where(Task.due_date == today).order_by(Task.id)).all()
    streak, week_done, week_total = _streak_stats(db, today)

    return ok(
        {
            "date": today.isoformat(),
            "apply_todo": [
                {"id": a.id, "company": a.company, "position": a.position, "city": a.city}
                for a in pending_apps
            ],
            "review_todo": review_todo,
            "question_todo": question_todo,
            "tasks": [TaskOut.model_validate(t).model_dump() for t in tasks_today],
            "streak": streak,
            "week_done": week_done,
            "week_total": week_total,
        }
    )


@router.get("/streak")
def dashboard_streak(db: Session = Depends(get_db)):
    today = date.today()
    streak, week_done, week_total = _streak_stats(db, today)
    return ok(
        {
            "streak": streak,
            "week_done": week_done,
            "week_total": week_total,
        }
    )