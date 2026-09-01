"""可校验的本地完整备份与恢复服务。"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import uuid
import zipfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath

from sqlalchemy import Date, DateTime, select
from sqlalchemy.orm import Session

from ..config import BACKUPS_DIR, DATA_DIR, FILES_DIR, settings
from ..core.errors import AppError
from ..database import ensure_dirs
from ..models import (
    Application,
    ApplicationStatusLog,
    Asset,
    Blacklist,
    Exam,
    ExamReview,
    Interview,
    InterviewQa,
    InterviewResult,
    JobType,
    Material,
    Offer,
    OfferWeightConfig,
    Question,
    Resume,
    ResumeLog,
    Script,
    Setting,
    Task,
)

BACKUP_FORMAT = "qiuzhao-room-backup"
BACKUP_SCHEMA_VERSION = 1

# 外键依赖顺序：先父后子。
TABLE_ORDER = [
    ("settings", Setting),
    ("offer_weight_config", OfferWeightConfig),
    ("job_types", JobType),
    ("resumes", Resume),
    ("resume_logs", ResumeLog),
    ("materials", Material),
    ("assets", Asset),
    ("applications", Application),
    ("application_status_logs", ApplicationStatusLog),
    ("offers", Offer),
    ("exams", Exam),
    ("exam_reviews", ExamReview),
    ("interviews", Interview),
    ("interview_qa", InterviewQa),
    ("interview_results", InterviewResult),
    ("questions", Question),
    ("scripts", Script),
    ("blacklist", Blacklist),
    ("tasks", Task),
]
ORDERED_NAMES = [name for name, _ in TABLE_ORDER]


def _dump_row(row, columns) -> dict:
    out = {}
    for col in columns:
        value = getattr(row, col.name)
        out[col.name] = value.isoformat() if isinstance(value, (datetime, date)) else value
    return out


def export_payload(db: Session) -> dict:
    tables: dict[str, list] = {}
    for name, model in TABLE_ORDER:
        pk_cols = list(model.__table__.primary_key.columns)
        rows = db.scalars(select(model).order_by(*pk_cols)).all()
        tables[name] = [_dump_row(row, model.__table__.columns) for row in rows]
    return {
        "format": BACKUP_FORMAT,
        "schema_version": BACKUP_SCHEMA_VERSION,
        "exported_at": datetime.now().isoformat(),
        "app_version": settings.app_version,
        "tables": tables,
        "files": [],
    }


def normalize_payload(body: dict) -> dict:
    """兼容旧接口响应外壳、旧 JSON 备份和新版完整备份。"""
    if not isinstance(body, dict):
        raise AppError(40000, "备份数据格式错误")
    if isinstance(body.get("data"), dict) and ("code" in body or "tables" not in body):
        body = body["data"]
    if "tables" not in body:
        body = {"tables": body}
    return body


def _validated_tables(payload: dict, *, require_all: bool) -> dict[str, list[dict]]:
    tables = payload.get("tables")
    if not isinstance(tables, dict):
        raise AppError(40000, "备份中缺少 tables 数据")

    unknown = [str(key) for key in tables if key not in ORDERED_NAMES]
    if unknown:
        raise AppError(40000, f"备份包含未知数据表：{', '.join(unknown)}")
    if require_all:
        missing = [name for name in ORDERED_NAMES if name not in tables]
        if missing:
            raise AppError(40000, f"完整备份缺少数据表：{', '.join(missing)}")

    result: dict[str, list[dict]] = {}
    model_map = dict(TABLE_ORDER)
    for name in ORDERED_NAMES:
        rows = tables.get(name, [])
        if not isinstance(rows, list):
            raise AppError(40000, f"数据表 {name} 应为数组")
        allowed_columns = {col.name for col in model_map[name].__table__.columns}
        clean_rows = []
        for index, raw in enumerate(rows):
            if not isinstance(raw, dict):
                raise AppError(40000, f"数据表 {name} 第 {index + 1} 行格式错误")
            extra = [str(key) for key in raw if key not in allowed_columns]
            if extra:
                raise AppError(40000, f"数据表 {name} 包含未知字段：{', '.join(extra)}")
            clean_rows.append(raw)
        result[name] = clean_rows
    return result


def _coerce(value, col_type, *, table: str, column: str):
    if value is None:
        return None
    if isinstance(col_type, DateTime) and isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise AppError(40000, f"{table}.{column} 的日期时间格式错误") from exc
    if isinstance(col_type, Date) and isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise AppError(40000, f"{table}.{column} 的日期格式错误") from exc
    return value


def replace_tables(db: Session, body: dict, *, require_all: bool = False) -> dict[str, int]:
    payload = normalize_payload(body)
    tables = _validated_tables(payload, require_all=require_all)

    for _name, model in reversed(TABLE_ORDER):
        db.query(model).delete()
    db.flush()

    counts: dict[str, int] = {}
    for name, model in TABLE_ORDER:
        rows = tables[name]
        for raw in rows:
            values = {
                col.name: _coerce(raw[col.name], col.type, table=name, column=col.name)
                for col in model.__table__.columns
                if col.name in raw
            }
            db.add(model(**values))
        db.flush()
        counts[name] = len(rows)
    return counts


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        while chunk := src.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _user_files() -> list[Path]:
    if not FILES_DIR.is_dir():
        return []
    return sorted(
        path
        for path in FILES_DIR.rglob("*")
        if path.is_file() and not path.is_relative_to((FILES_DIR / "cache").resolve())
    )


def create_archive(db: Session, target: Path) -> Path:
    """创建包含表数据、用户上传文件、大小和 SHA-256 的 ZIP 备份。"""
    ensure_dirs()
    payload = export_payload(db)
    files = _user_files()
    payload["files"] = [
        {
            "path": path.relative_to(FILES_DIR).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("backup.json", json.dumps(payload, ensure_ascii=False, indent=2))
        for path in files:
            archive.write(path, f"files/{path.relative_to(FILES_DIR).as_posix()}")
    return target


def create_temporary_export(db: Session) -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    handle, filename = tempfile.mkstemp(prefix=".export-", suffix=".zip", dir=BACKUPS_DIR)
    os.close(handle)
    Path(filename).unlink(missing_ok=True)
    return create_archive(db, Path(filename))


def _create_auto_snapshot(db: Session) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    target = BACKUPS_DIR / f"auto-before-restore-{stamp}.zip"
    create_archive(db, target)
    snapshots = sorted(BACKUPS_DIR.glob("auto-before-restore-*.zip"), key=lambda p: p.stat().st_mtime)
    for old in snapshots[:-max(settings.auto_backup_keep, 1)]:
        old.unlink(missing_ok=True)
    return target


async def save_uploaded_archive(upload) -> Path:
    if not (upload.filename or "").lower().endswith(".zip"):
        raise AppError(40000, "请选择由本软件导出的 ZIP 备份")
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    handle, filename = tempfile.mkstemp(prefix=".import-", suffix=".zip", dir=BACKUPS_DIR)
    max_bytes = settings.max_backup_mb * 1024 * 1024
    size = 0
    try:
        with open(handle, "wb", closefd=True) as out:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise AppError(40000, f"备份包超过大小限制（{settings.max_backup_mb}MB）")
                out.write(chunk)
        return Path(filename)
    except Exception:
        Path(filename).unlink(missing_ok=True)
        raise


def _safe_member(info: zipfile.ZipInfo) -> PurePosixPath:
    path = PurePosixPath(info.filename)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise AppError(40000, "备份包包含不安全的文件路径")
    mode = info.external_attr >> 16
    if mode & 0o170000 == 0o120000:
        raise AppError(40000, "备份包不能包含符号链接")
    if path.as_posix() != "backup.json" and path.parts[0] != "files":
        raise AppError(40000, f"备份包包含未知内容：{path.as_posix()}")
    return path


def _load_archive(archive_path: Path, stage_files: Path) -> dict:
    if not zipfile.is_zipfile(archive_path):
        raise AppError(40000, "备份包不是有效的 ZIP 文件")
    max_uncompressed = settings.max_backup_mb * 2 * 1024 * 1024
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) > 10000 or sum(info.file_size for info in infos) > max_uncompressed:
            raise AppError(40000, "备份包解压内容异常或过大")
        paths = {_safe_member(info).as_posix(): info for info in infos}
        if "backup.json" not in paths:
            raise AppError(40000, "备份包缺少 backup.json")
        bad = archive.testzip()
        if bad:
            raise AppError(40000, f"备份包校验失败：{bad}")
        try:
            payload = json.loads(archive.read("backup.json").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AppError(40000, "backup.json 格式损坏") from exc

        payload = normalize_payload(payload)
        if payload.get("format") != BACKUP_FORMAT or payload.get("schema_version") != BACKUP_SCHEMA_VERSION:
            raise AppError(40000, "备份格式或版本不受支持")
        _validated_tables(payload, require_all=True)

        manifest = payload.get("files")
        if not isinstance(manifest, list):
            raise AppError(40000, "备份文件清单缺失")
        expected: dict[str, dict] = {}
        for item in manifest:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                raise AppError(40000, "备份文件清单格式错误")
            rel = PurePosixPath(item["path"])
            if rel.is_absolute() or ".." in rel.parts:
                raise AppError(40000, "备份文件清单包含不安全路径")
            expected[rel.as_posix()] = item

        actual = {
            PurePosixPath(*PurePosixPath(name).parts[1:]).as_posix()
            for name in paths
            if name.startswith("files/") and not paths[name].is_dir()
        }
        if actual != set(expected):
            raise AppError(40000, "备份文件清单与压缩包内容不一致")

        stage_files.mkdir(parents=True, exist_ok=True)
        for rel_name, item in expected.items():
            info = paths[f"files/{rel_name}"]
            destination = (stage_files / Path(rel_name)).resolve()
            if not destination.is_relative_to(stage_files.resolve()):
                raise AppError(40000, "备份文件路径越界")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, destination.open("wb") as out:
                shutil.copyfileobj(src, out, length=1024 * 1024)
            if destination.stat().st_size != item.get("size") or _sha256(destination) != item.get("sha256"):
                raise AppError(40000, f"备份文件校验失败：{rel_name}")
        return payload


def restore_archive(db: Session, archive_path: Path) -> dict:
    """完整校验后恢复数据库与文件，异常时恢复原文件目录并回滚事务。"""
    ensure_dirs()
    with tempfile.TemporaryDirectory(prefix=".restore-", dir=DATA_DIR) as tmp:
        stage_files = Path(tmp) / "files"
        payload = _load_archive(archive_path, stage_files)
        snapshot = _create_auto_snapshot(db)
        counts = replace_tables(db, payload, require_all=True)

        old_files = DATA_DIR / f".files-before-restore-{uuid.uuid4().hex}"
        swapped = False
        try:
            if FILES_DIR.exists():
                FILES_DIR.rename(old_files)
            stage_files.rename(FILES_DIR)
            swapped = True
            ensure_dirs()
            db.commit()
        except Exception:
            db.rollback()
            if swapped and FILES_DIR.exists():
                shutil.rmtree(FILES_DIR)
            if old_files.exists():
                old_files.rename(FILES_DIR)
            ensure_dirs()
            raise
        else:
            if old_files.exists():
                shutil.rmtree(old_files)
        return {"imported": counts, "snapshot": snapshot.name}
