"""全局配置。

- BASE_DIR: backend 目录（相对路径的基准）
- DATA_DIR: 运行时数据目录（SQLite + 上传文件）

项目是本地个人软件。默认仅允许本机前端访问 API，同时保留旧版
``MSHOP_DATA_DIR`` 环境变量，避免已有用户的数据目录配置失效。
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(
    os.environ.get("QIUZHAO_DATA_DIR")
    or os.environ.get("MSHOP_DATA_DIR")
    or (BASE_DIR / "data")
).resolve()
DB_PATH = DATA_DIR / "app.db"
FILES_DIR = DATA_DIR / "files"
CACHE_DIR = FILES_DIR / "cache"
BACKUPS_DIR = DATA_DIR / "backups"
FRONTEND_DIST = BASE_DIR / "web"


def _desktop_origin_from_env() -> str | None:
    """读取 Electron 为本次启动分配的本机来源，仅接受 127.0.0.1 动态端口。"""
    raw = os.environ.get("QIUZHAO_DESKTOP_ORIGIN", "").strip().rstrip("/")
    if not raw:
        return None
    try:
        parsed = urlsplit(raw)
        if (
            parsed.scheme == "http"
            and parsed.hostname == "127.0.0.1"
            and parsed.port is not None
            and not parsed.username
            and not parsed.password
            and parsed.path in ("", "/")
            and not parsed.query
            and not parsed.fragment
        ):
            return f"http://127.0.0.1:{parsed.port}"
    except ValueError:
        pass
    return None


DESKTOP_ORIGIN = _desktop_origin_from_env()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MSHOP_", extra="ignore")

    app_name: str = "秋招辅助管理后端"
    app_version: str = "1.0.0"
    database_url: str = f"sqlite:///{DB_PATH.as_posix()}"
    # 只允许本机开发、预览和同源部署端口访问，防止任意网页调用本地 API。
    cors_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ] + ([DESKTOP_ORIGIN] if DESKTOP_ORIGIN else [])
    allowed_hosts: list[str] = ["127.0.0.1", "localhost", "::1", "testserver"]
    # 删除简历/资产时是否同步删除落盘文件（可配置）
    file_delete_on_remove: bool = True
    # 上传大小上限（单位 MB）
    max_upload_mb: int = 50
    # 备份包上限及自动恢复点保留数量
    max_backup_mb: int = 1024
    auto_backup_keep: int = 5

settings = Settings()
