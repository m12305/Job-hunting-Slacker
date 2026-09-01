"""统计聚合服务（模块四）。

口径（《PRD》7.1）：
- 总投递数：全部投递记录
- 有效投递数：排除「待投递 pending」
- 挂简历率：挂简历数 / 有效投递数
- 笔试通过率：复盘通过数 / 已复盘笔试数
- 面试率：进入面试投递数 / 有效投递数
- Offer 率：offer 记录数 / 有效投递数
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import (
    Application,
    ApplicationStatusLog,
    Exam,
    ExamReview,
    Interview,
    JobType,
    Offer,
    Question,
)

EXAM_REACHED = {"exam", "interview", "offered", "rejected"}
INTERVIEW_REACHED = {"interview", "offered", "rejected"}
OFFER_REACHED = {"offered", "rejected"}


def _entered_ids(db: Session, to_status: str) -> set[int]:
    """状态流水与当前状态取并集，兼容新旧数据混合和手工导入记录。"""
    from_logs = set(
        db.scalars(
            select(ApplicationStatusLog.application_id).where(ApplicationStatusLog.to_status == to_status)
        )
    )
    statuses = {
        "exam": EXAM_REACHED,
        "interview": INTERVIEW_REACHED,
        "offered": OFFER_REACHED,
    }[to_status]
    from_current = set(db.scalars(select(Application.id).where(Application.status.in_(statuses))))
    if to_status == "exam":
        from_current.update(
            db.scalars(
                select(Application.id).where(
                    Application.close_reason.in_(["exam_failed", "employer_rejected", "offer_declined"])
                )
            )
        )
    elif to_status == "interview":
        from_current.update(
            db.scalars(
                select(Application.id).where(
                    Application.close_reason.in_(["employer_rejected", "offer_declined"])
                )
            )
        )
    return from_logs | from_current


def _effective_applications(db: Session) -> int:
    return db.scalar(
        select(func.count(Application.id)).where(Application.status != "pending")
    ) or 0


def overview(db: Session) -> dict:
    total = db.scalar(select(func.count(Application.id))) or 0
    effective = _effective_applications(db)
    resume_rejected_ids = set(
        db.scalars(
            select(Application.id).where(
                (Application.status == "resume_rejected") | (Application.close_reason == "resume_rejected")
            )
        )
    )
    resume_rejected_ids.update(
        db.scalars(
            select(ApplicationStatusLog.application_id).where(
                ApplicationStatusLog.to_status == "resume_rejected"
            )
        )
    )

    # 笔试通过率：已复盘（passed 有值）中通过的比例
    reviewed = db.scalar(
        select(func.count(ExamReview.id)).where(ExamReview.passed.is_not(None))
    ) or 0
    reviewed_passed = db.scalar(
        select(func.count(ExamReview.id)).where(ExamReview.passed.is_(True))
    ) or 0

    entered_interview = len(_entered_ids(db, "interview"))
    offered_ids = _entered_ids(db, "offered")
    offered_ids.update(
        db.scalars(select(Offer.application_id).where(Offer.application_id.is_not(None)))
    )

    def rate(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0

    return {
        "total_applications": total,
        "effective_applications": effective,
        "resume_rejected_rate": rate(len(resume_rejected_ids), effective),
        "exam_pass_rate": rate(reviewed_passed, reviewed),
        "interview_rate": rate(entered_interview, effective),
        "offer_rate": rate(len(offered_ids), effective),
    }


def by_job_type(db: Session) -> list[dict]:
    rows = db.execute(
        select(Application, JobType.name)
        .outerjoin(JobType, Application.job_type_id == JobType.id)
        .order_by(Application.id)
    ).all()

    groups: dict[str, list[Application]] = {}
    for app, type_name in rows:
        groups.setdefault(type_name or "未分类", []).append(app)

    exam_ids = _entered_ids(db, "exam")
    interview_ids = _entered_ids(db, "interview")
    offer_app_ids = _entered_ids(db, "offered")
    offer_app_ids.update(db.scalars(select(Offer.application_id).where(Offer.application_id.is_not(None))))

    result = []
    for type_name, apps in groups.items():
        total = len(apps)
        effective = sum(1 for a in apps if a.status != "pending")
        exam_count = sum(1 for a in apps if a.id in exam_ids)
        interview_count = sum(1 for a in apps if a.id in interview_ids)
        offer_count = sum(1 for a in apps if a.id in offer_app_ids)
        result.append(
            {
                "job_type": type_name,
                "total_applications": total,
                "effective_applications": effective,
                "exam_count": exam_count,
                "interview_count": interview_count,
                "offer_count": offer_count,
                "exam_rate": round(exam_count / effective, 4) if effective else 0.0,
                "interview_rate": round(interview_count / effective, 4) if effective else 0.0,
                "offer_rate": round(offer_count / effective, 4) if effective else 0.0,
            }
        )
    result.sort(key=lambda r: -r["total_applications"])
    return result


def by_time(db: Session, granularity: str, start: date | None, end: date | None) -> dict:
    apps = db.scalars(select(Application).order_by(Application.id)).all()
    buckets: dict[str, int] = {}
    for app in apps:
        if app.status == "pending":
            continue
        dt = app.apply_time
        if dt is None:
            continue
        day = dt.date()
        if start and day < start:
            continue
        if end and day > end:
            continue
        key = _bucket(dt, granularity)
        buckets[key] = buckets.get(key, 0) + 1
    items = [{"label": key, "count": buckets[key]} for key in sorted(buckets.keys())]
    return {"granularity": granularity, "items": items}


def _bucket(dt: datetime, granularity: str) -> str:
    if granularity == "day":
        return dt.strftime("%Y-%m-%d")
    if granularity == "week":
        iso = dt.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    return dt.strftime("%Y-%m")
