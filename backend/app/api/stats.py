"""统计接口（模块四）。"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..core.response import ok
from ..database import get_db
from ..services import stats_service

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return ok(stats_service.overview(db))


@router.get("/by-job-type")
def get_by_job_type(db: Session = Depends(get_db)):
    return ok(stats_service.by_job_type(db))


@router.get("/by-time")
def get_by_time(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    return ok(stats_service.by_time(db, granularity, start, end))