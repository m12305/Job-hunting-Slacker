"""API 路由汇总。"""
from fastapi import APIRouter

from . import (
    applications,
    assets,
    blacklist,
    dashboard,
    exams,
    interview_qa,
    interviews,
    job_types,
    materials,
    offer_weight_config,
    offers,
    questions,
    resume_logs,
    resumes,
    scripts,
    stats,
    system,
    tasks,
)

api_router = APIRouter()
api_router.include_router(job_types.router)
api_router.include_router(resumes.router)
api_router.include_router(resume_logs.router)
api_router.include_router(materials.router)
api_router.include_router(assets.router)
api_router.include_router(applications.router)
api_router.include_router(offers.router)
api_router.include_router(offer_weight_config.router)
api_router.include_router(exams.router)
api_router.include_router(interviews.router)
api_router.include_router(interview_qa.router)
api_router.include_router(questions.router)
api_router.include_router(stats.router)
api_router.include_router(scripts.router)
api_router.include_router(blacklist.router)
api_router.include_router(tasks.router)
api_router.include_router(dashboard.router)
api_router.include_router(system.router)