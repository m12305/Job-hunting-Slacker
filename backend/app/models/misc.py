"""模块五：话术库 / 黑名单 / 每日任务 / 键值设置。"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Script(Base, TimestampMixin):
    """话术库（6.1）。"""

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Blacklist(Base, TimestampMixin):
    """黑名单/避雷库（6.2）。"""

    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    position: Mapped[str | None] = mapped_column(String(200))
    issue_type: Mapped[str | None] = mapped_column(String(50), index=True)
    detail: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200))


class Task(Base, TimestampMixin):
    """每日任务（6.3）。"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    ref_id: Mapped[int | None] = mapped_column(Integer)
    ref_type: Mapped[str | None] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime)


class Setting(Base):
    """键值配置（6.4）。"""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)  # JSON 字符串