"""投递记录 CRUD + 状态机 + 状态流水（模块二）。"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from ..core.constants import STATUS_TRANSITIONS
from ..core.errors import AppError
from ..core.response import ok, page_data
from ..crud.base import get_or_404
from ..database import get_db
from ..models import (
    Application,
    ApplicationStatusLog,
    Blacklist,
    Exam,
    Interview,
    JobType,
    Offer,
    Resume,
)
from ..schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    StatusChangeIn,
    StatusLogOut,
)
from ..services.application_service import change_status

router = APIRouter(prefix="/api/applications", tags=["投递记录"])

STATUS_GROUPS: dict[str, list[str]] = {
    "pending": ["pending"],
    "applied": ["applied", "resume_screening"],
    "exam": ["exam"],
    "interview": ["interview"],
    "closed": ["resume_rejected", "ended", "rejected"],
    "offered": ["offered"],
}


def _to_out(db: Session, app: Application) -> ApplicationOut:
    out = ApplicationOut.model_validate(app)
    if app.job_type_id:
        jt = db.get(JobType, app.job_type_id)
        out.job_type_name = jt.name if jt else None
    if app.resume_version_id:
        rs = db.get(Resume, app.resume_version_id)
        out.resume_version_name = rs.version_name if rs else None
    return out


@router.get("")
def list_applications(
    status: str | None = None,
    status_group: str | None = Query(None, pattern="^(pending|applied|exam|interview|closed|offered)$"),
    company: str | None = None,
    position: str | None = None,
    city: str | None = None,
    channel: str | None = None,
    job_type_id: int | None = None,
    keyword: str | None = None,
    apply_time_range: str | None = Query(None, pattern="^(last_7_days|last_30_days|older|missing)$"),
    apply_time_from: date | None = None,
    apply_time_to: date | None = None,
    sort_by: str = Query("apply_time", pattern="^(apply_time|updated_at|company|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    conds = []
    if status:
        conds.append(Application.status == status)
    elif status_group:
        conds.append(Application.status.in_(STATUS_GROUPS[status_group]))
    if company:
        conds.append(Application.company.icontains(company.strip(), autoescape=True))
    if position:
        conds.append(Application.position.icontains(position.strip(), autoescape=True))
    if city:
        conds.append(Application.city.icontains(city.strip(), autoescape=True))
    if channel:
        conds.append(Application.channel == channel)
    if job_type_id:
        conds.append(Application.job_type_id == job_type_id)
    if keyword:
        value = keyword.strip()
        conds.append(
            or_(
                Application.company.icontains(value, autoescape=True),
                Application.position.icontains(value, autoescape=True),
                Application.city.icontains(value, autoescape=True),
                Application.remark.icontains(value, autoescape=True),
            )
        )

    now = datetime.now()
    if apply_time_range == "last_7_days":
        conds.append(Application.apply_time >= now - timedelta(days=7))
    elif apply_time_range == "last_30_days":
        conds.append(Application.apply_time >= now - timedelta(days=30))
    elif apply_time_range == "older":
        conds.append(Application.apply_time < now - timedelta(days=30))
    elif apply_time_range == "missing":
        conds.append(Application.apply_time.is_(None))
    if apply_time_from:
        conds.append(Application.apply_time >= datetime.combine(apply_time_from, time.min))
    if apply_time_to:
        conds.append(Application.apply_time < datetime.combine(apply_time_to + timedelta(days=1), time.min))

    base = (
        select(Application, JobType.name, Resume.version_name)
        .outerjoin(JobType, Application.job_type_id == JobType.id)
        .outerjoin(Resume, Application.resume_version_id == Resume.id)
    )
    if conds:
        base = base.where(*conds)
    total = db.scalar(select(func.count(Application.id)).where(*conds)) or 0

    sort_column = {
        "apply_time": Application.apply_time,
        "updated_at": Application.updated_at,
        "company": Application.company,
        "status": Application.status,
    }[sort_by]
    sort_expr = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    nulls_last = case((sort_column.is_(None), 1), else_=0) if sort_by == "apply_time" else None
    order = ([nulls_last] if nulls_last is not None else []) + [sort_expr, Application.id.desc()]
    rows = db.execute(
        base.order_by(*order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = []
    for app, job_type_name, resume_version_name in rows:
        out = ApplicationOut.model_validate(app)
        out.job_type_name = job_type_name
        out.resume_version_name = resume_version_name
        items.append(out.model_dump())

    facet_conds = [cond for cond in conds if not _is_status_condition(cond)]
    facet_rows = db.execute(
        select(Application.status, func.count(Application.id))
        .where(*facet_conds)
        .group_by(Application.status)
    ).all()
    exact_counts = {value: count for value, count in facet_rows}
    facets = {key: sum(exact_counts.get(value, 0) for value in values) for key, values in STATUS_GROUPS.items()}
    facets["all"] = sum(exact_counts.values())

    data = page_data(items, total, page, page_size)
    data["facets"] = facets
    return ok(data)


def _is_status_condition(condition) -> bool:
    """列表 facets 需要忽略当前状态条件，其余搜索和时间条件继续生效。"""
    left = getattr(condition, "left", None)
    return getattr(left, "name", None) == "status" and getattr(left, "table", None) is Application.__table__


@router.get("/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    app = get_or_404(db, Application, application_id, "投递记录")
    logs = db.scalars(
        select(ApplicationStatusLog)
        .where(ApplicationStatusLog.application_id == application_id)
        .order_by(ApplicationStatusLog.changed_at.desc(), ApplicationStatusLog.id.desc())
    ).all()
    exams = db.scalars(
        select(Exam).where(Exam.application_id == application_id).order_by(Exam.id.desc())
    ).all()
    interviews = db.scalars(
        select(Interview).where(Interview.application_id == application_id).order_by(Interview.id.desc())
    ).all()
    offers = db.scalars(
        select(Offer).where(Offer.application_id == application_id).order_by(Offer.id.desc())
    ).all()
    blacklist_hits = db.scalar(
        select(func.count(Blacklist.id)).where(
            func.lower(func.trim(Blacklist.company)) == app.company.strip().lower()
        )
    ) or 0

    data = _to_out(db, app).model_dump()
    data["timeline"] = [StatusLogOut.model_validate(x).model_dump() for x in logs]
    data["exams"] = [
        {"id": e.id, "exam_time": e.exam_time, "platform": e.platform, "status": e.status} for e in exams
    ]
    data["interviews"] = [
        {
            "id": i.id,
            "round": i.round,
            "interview_time": i.interview_time,
            "status": i.status,
        }
        for i in interviews
    ]
    data["offers"] = [
        {
            "id": o.id,
            "company": o.company,
            "position": o.position,
            "salary_base": o.salary_base,
            "status": o.status,
        }
        for o in offers
    ]
    data["blacklist_hits"] = blacklist_hits
    return ok(data)


@router.post("")
def create_application(body: ApplicationCreate, db: Session = Depends(get_db)):
    if body.resume_version_id:
        get_or_404(db, Resume, body.resume_version_id, "简历版本")
    if body.job_type_id:
        get_or_404(db, JobType, body.job_type_id, "岗位类型")
    initial_status = body.status or "pending"
    if initial_status not in STATUS_TRANSITIONS:
        raise AppError(40000, f"未知的投递状态：{initial_status}")

    data = body.model_dump()
    for key in ("company", "position", "city", "channel", "source_url", "remark"):
        if isinstance(data.get(key), str):
            data[key] = data[key].strip() or None
    if not data.get("company") or not data.get("position"):
        raise AppError(40000, "公司和岗位不能为空")
    data["status"] = initial_status
    if initial_status == "resume_rejected":
        data["close_reason"] = "resume_rejected"
        data["closed_at"] = datetime.now()
    elif initial_status == "rejected":
        data["close_reason"] = "offer_declined"
        data["closed_at"] = datetime.now()
    elif initial_status == "ended":
        data["close_reason"] = data.get("close_reason") or "other"
        data["closed_at"] = datetime.now()
    else:
        data["close_reason"] = None
        data["closed_at"] = None
    row = Application(**data)
    db.add(row)
    db.flush()

    db.add(
        ApplicationStatusLog(
            application_id=row.id,
            from_status=None,
            to_status=initial_status,
            close_reason=row.close_reason,
            note="创建投递记录",
            changed_at=datetime.now(),
        )
    )
    return ok(_to_out(db, row))


@router.put("/{application_id}")
def update_application(application_id: int, body: ApplicationUpdate, db: Session = Depends(get_db)):
    row = get_or_404(db, Application, application_id, "投递记录")
    data = body.model_dump(exclude_unset=True)
    if data.get("resume_version_id"):
        get_or_404(db, Resume, data["resume_version_id"], "简历版本")
    if data.get("job_type_id"):
        get_or_404(db, JobType, data["job_type_id"], "岗位类型")
    for key in ("company", "position", "city", "channel", "source_url", "remark"):
        if isinstance(data.get(key), str):
            data[key] = data[key].strip() or None
    if "company" in data and not data["company"] or "position" in data and not data["position"]:
        raise AppError(40000, "公司和岗位不能为空")
    salary_min = data.get("salary_min", row.salary_min)
    salary_max = data.get("salary_max", row.salary_max)
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise AppError(40000, "薪资下限不能高于上限")
    for key, value in data.items():
        setattr(row, key, value)
    db.flush()
    return ok(_to_out(db, row))


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    row = get_or_404(db, Application, application_id, "投递记录")
    db.delete(row)
    db.flush()
    return ok(None)


@router.put("/{application_id}/status")
def update_application_status(
    application_id: int,
    body: StatusChangeIn,
    db: Session = Depends(get_db),
):
    row = get_or_404(db, Application, application_id, "投递记录")
    changed = change_status(db, row, body.to_status, body.note, body.close_reason)
    db.flush()
    data = _to_out(db, row).model_dump()
    data["changed"] = changed
    return ok(data)


@router.get("/{application_id}/timeline")
def get_application_timeline(application_id: int, db: Session = Depends(get_db)):
    get_or_404(db, Application, application_id, "投递记录")
    rows = db.scalars(
        select(ApplicationStatusLog)
        .where(ApplicationStatusLog.application_id == application_id)
        .order_by(ApplicationStatusLog.changed_at.desc(), ApplicationStatusLog.id.desc())
    ).all()
    return ok([StatusLogOut.model_validate(r) for r in rows])
