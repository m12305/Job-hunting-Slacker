"""模块一：岗位类型 / 简历版本 / 修改日志 / 素材库 / 资产归档。"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class JobType(Base, TimestampMixin):
    """岗位类型（3.1）。"""

    __tablename__ = "job_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Resume(Base, TimestampMixin):
    """简历版本（3.2）。"""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_types.id", ondelete="RESTRICT"), index=True
    )
    version_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_position: Mapped[str | None] = mapped_column(String(100))
    file_path: Mapped[str | None] = mapped_column(String(500))  # 相对 backend 根目录
    file_name: Mapped[str | None] = mapped_column(String(255))
    file_type: Mapped[str | None] = mapped_column(String(10))  # pdf/doc/docx
    file_size: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text)


class ResumeLog(Base):
    """简历修改日志（3.3）。"""

    __tablename__ = "resume_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_version_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    change_desc: Mapped[str] = mapped_column(Text, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)


class Material(Base, TimestampMixin):
    """个人素材库（3.4）。"""

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(200))
    role: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)  # STAR 结构化描述
    highlights: Mapped[str | None] = mapped_column(Text)   # 亮点/量化成果
    tech_stack: Mapped[list | None] = mapped_column(JSON, default=list)
    attachments: Mapped[list | None] = mapped_column(JSON, default=list)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)


class Asset(Base, TimestampMixin):
    """作品集/证书/成绩单归档（3.5）。"""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(String(500))
    file_path: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)