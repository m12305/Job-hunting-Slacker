"""文件存储与转换服务。

文件一律落盘到 data/files/{分类}/ 下，数据库仅存相对 backend 根目录的路径。
"""
from __future__ import annotations

import shutil
import subprocess
import uuid
import logging
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import event
from sqlalchemy.orm import Session

from ..config import BASE_DIR, CACHE_DIR, FILES_DIR, settings
from ..core.errors import AppError

logger = logging.getLogger("qiuzhao-room.storage")
_PENDING_DELETE_KEY = "qiuzhao_pending_file_deletes"

# 资产分类 -> 存储子目录
CATEGORY_DIRS = {
    "resumes": "resumes",
    "certificate": "certificates",
    "transcript": "certificates",
    "assets": "assets",
    "audios": "audios",
}

ALLOWED_EXT = {
    "pdf", "doc", "docx", "png", "jpg", "jpeg", "webp", "gif",
    "mp3", "m4a", "wav", "zip",
}

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "wav": "audio/wav",
    "zip": "application/zip",
}


def ext_of(filename: str) -> str:
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def abs_of(rel: str) -> Path:
    """解析新旧数据库路径，并强制限制在当前 ``FILES_DIR`` 内。"""
    if not rel or Path(rel).is_absolute():
        raise AppError(40000, "文件路径无效")
    files_root = FILES_DIR.resolve()
    rel_path = Path(rel)

    # 旧版本保存为相对 backend 的 data/files/...，优先兼容已有记录。
    legacy = (BASE_DIR / rel_path).resolve()
    if legacy.is_relative_to(files_root):
        return legacy

    # 新版本始终保存为相对 FILES_DIR 的路径，支持把数据目录放到任意磁盘。
    path = (files_root / rel_path).resolve()
    if path.is_relative_to(files_root):
        return path

    raise AppError(40000, "文件路径越出本地数据目录，已拒绝访问")


def rel_of(abs_path: Path) -> str:
    path = abs_path.resolve()
    if not path.is_relative_to(FILES_DIR.resolve()):
        raise AppError(40000, "只能保存本地数据目录内的文件")
    return path.relative_to(FILES_DIR.resolve()).as_posix()


def media_type(file_type: str | None) -> str:
    return MEDIA_TYPES.get(file_type or "", "application/octet-stream")


async def save_upload(category: str, upload: UploadFile, prefix: str = "") -> tuple[str, int]:
    """保存上传文件，返回 (相对路径, 字节数)。"""
    ext = ext_of(upload.filename or "")
    if ext not in ALLOWED_EXT:
        raise AppError(40000, f"不支持的文件类型：{ext or '未知'}")

    sub = CATEGORY_DIRS.get(category, "assets")
    target_dir = FILES_DIR / sub
    target_dir.mkdir(parents=True, exist_ok=True)

    fname = f"{prefix}-{uuid.uuid4().hex[:10]}.{ext}" if prefix else f"{uuid.uuid4().hex[:10]}.{ext}"
    target = target_dir / fname

    max_bytes = settings.max_upload_mb * 1024 * 1024
    size = 0
    try:
        with target.open("wb") as out:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise AppError(40000, f"文件超过大小限制（{settings.max_upload_mb}MB）")
                out.write(chunk)
        _validate_file_signature(target, ext)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return rel_of(target), size


def _validate_file_signature(path: Path, ext: str) -> None:
    """做轻量文件头校验，避免仅修改扩展名的文件进入预览或解压流程。"""
    with path.open("rb") as src:
        head = src.read(32)
    valid = {
        "pdf": head.startswith(b"%PDF-"),
        "doc": head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")),
        "docx": head.startswith(b"PK"),
        "zip": head.startswith(b"PK"),
        "png": head.startswith(b"\x89PNG\r\n\x1a\n"),
        "jpg": head.startswith(b"\xff\xd8\xff"),
        "jpeg": head.startswith(b"\xff\xd8\xff"),
        "gif": head.startswith((b"GIF87a", b"GIF89a")),
        "webp": head.startswith(b"RIFF") and head[8:12] == b"WEBP",
        "wav": head.startswith(b"RIFF") and head[8:12] == b"WAVE",
        "m4a": len(head) >= 12 and head[4:8] == b"ftyp",
        "mp3": head.startswith(b"ID3") or (len(head) >= 2 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0),
    }.get(ext, True)
    if not valid:
        raise AppError(40000, "文件内容与扩展名不匹配")


def delete_file(rel: str | None) -> None:
    if not rel:
        return
    try:
        p = abs_of(rel)
        if p.is_file():
            p.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("删除文件失败 %s: %s", rel, exc)


def queue_file_delete(db: Session, rel: str | None) -> None:
    """数据库事务成功提交后再清理文件，避免提交失败造成原文件丢失。"""
    if rel:
        db.info.setdefault(_PENDING_DELETE_KEY, set()).add(rel)


@event.listens_for(Session, "after_commit")
def _delete_queued_files(session: Session) -> None:
    for rel in session.info.pop(_PENDING_DELETE_KEY, set()):
        try:
            delete_file(rel)
        except AppError as exc:
            logger.warning("跳过不安全的待删除路径 %s: %s", rel, exc)


@event.listens_for(Session, "after_rollback")
def _clear_queued_files(session: Session) -> None:
    session.info.pop(_PENDING_DELETE_KEY, None)


def _find_soffice() -> str | None:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if exe:
        return exe
    candidates = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
        Path("/usr/bin/soffice"),
        Path("/usr/local/bin/soffice"),
        Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def convert_to_pdf(src_abs: Path, out_dir: Path) -> Path | None:
    """调用 LibreOffice headless 将 Word 转为 PDF；不可用时返回 None。"""
    soffice = _find_soffice()
    if not soffice:
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(src_abs)]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=180)
        if proc.returncode != 0:
            return None
    except Exception:
        return None
    pdf = out_dir / f"{src_abs.stem}.pdf"
    return pdf if pdf.is_file() else None


def preview_cache_path(resume_id: int) -> Path:
    return CACHE_DIR / f"resume{resume_id}.pdf"
