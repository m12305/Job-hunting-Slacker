"""数据库引擎与会话管理。"""
from __future__ import annotations

from collections.abc import Generator

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from .config import BACKUPS_DIR, BASE_DIR, DATA_DIR, FILES_DIR, settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
    """SQLite 默认不强制外键，此处开启以支持 RESTRICT/CASCADE。"""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


def ensure_dirs() -> None:
    """创建运行时目录：SQLite 所在目录 + 文件存储分类目录。"""
    for sub in ("resumes", "certificates", "assets", "audios", "cache"):
        (FILES_DIR / sub).mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def run_migrations() -> None:
    """启动时自动升级到最新数据库结构，避免代码与本地数据库版本不一致。"""
    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BASE_DIR / "alembic"))
    command.upgrade(config, "head")


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：请求内会话，成功自动提交，异常回滚。"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
