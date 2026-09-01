"""FastAPI 应用入口。

启动：cd backend && uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.router import api_router
from .config import FRONTEND_DIST, settings
from .core.errors import register_exception_handlers
from .database import SessionLocal, ensure_dirs, run_migrations
from .services.seed import ensure_seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dirs()
    run_migrations()
    with SessionLocal() as db:
        ensure_seed(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="秋招辅助管理软件后端 API（FastAPI + SQLAlchemy + SQLite）",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type"],
)


@app.middleware("http")
async def local_request_guard(request: Request, call_next):
    """拒绝非本机 Host 或未知网页 Origin，命令行和桌面端无 Origin 请求仍可用。"""
    hostname = request.url.hostname or ""
    if hostname not in settings.allowed_hosts:
        return JSONResponse(
            status_code=403,
            content={"code": 40300, "message": "仅允许从本机访问该服务", "data": None},
        )

    origin = request.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        return JSONResponse(
            status_code=403,
            content={"code": 40300, "message": "该网页无权访问本地求职数据", "data": None},
        )
    return await call_next(request)

app.include_router(api_router)
register_exception_handlers(app)


def _register_packaged_frontend(frontend_dir: Path) -> None:
    """桌面发行版中由 FastAPI 托管 Vite 产物，并为 Vue history 路由回退。"""
    index_file = frontend_dir / "index.html"
    assets_dir = frontend_dir / "assets"
    if not index_file.is_file():
        return

    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def desktop_index():
        return FileResponse(index_file)

    @app.get("/{full_path:path}", include_in_schema=False)
    def desktop_spa(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = (frontend_dir / full_path).resolve()
        if candidate.is_relative_to(frontend_dir.resolve()) and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_file)


_register_packaged_frontend(FRONTEND_DIST)
