"""系统接口：健康检查、设置、完整备份与兼容导入导出。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from ..config import settings
from ..core.response import ok
from ..database import get_db
from ..services.backup_service import (
    create_temporary_export,
    export_payload,
    replace_tables,
    restore_archive,
    save_uploaded_archive,
)
from ..services.settings_service import get_settings_map, set_settings

router = APIRouter(prefix="/api", tags=["系统"])

@router.get("/health")
def health_check():
    return ok(
        {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
            "time": datetime.now().isoformat(),
        }
    )


@router.get("/settings")
def read_settings(db: Session = Depends(get_db)):
    return ok(get_settings_map(db))


@router.put("/settings")
def write_settings(body: dict, db: Session = Depends(get_db)):
    set_settings(db, body)
    db.flush()
    return ok(get_settings_map(db))


@router.get("/export")
def export_all(db: Session = Depends(get_db)):
    """兼容旧版 JSON 导出；新界面默认使用包含文件的 ZIP 备份。"""
    return ok(export_payload(db))


@router.post("/import")
def import_all(body: dict, db: Session = Depends(get_db)):
    """兼容旧版 JSON 覆盖导入，支持旧响应外壳并严格校验字段与日期。"""
    counts = replace_tables(db, body)
    return ok({"imported": counts})


@router.get("/backup/export")
def export_backup_archive(db: Session = Depends(get_db)):
    archive = create_temporary_export(db)
    filename = f"qiuzhao-backup-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.zip"
    return FileResponse(
        archive,
        media_type="application/zip",
        filename=filename,
        background=BackgroundTask(archive.unlink, missing_ok=True),
    )


@router.post("/backup/import")
async def import_backup_archive(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    archive = await save_uploaded_archive(file)
    try:
        result = restore_archive(db, archive)
        return ok(result)
    finally:
        archive.unlink(missing_ok=True)
