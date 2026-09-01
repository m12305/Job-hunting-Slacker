"""模块五：话术 / 黑名单 / 任务 / 设置 / 看板。"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from .common import ORMModel


# ---------- 话术库 ----------
class ScriptCreate(BaseModel):
    category: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    tags: list[str] | None = None
    is_favorite: bool = False


class ScriptUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=30)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    is_favorite: bool | None = None


class FavoriteIn(BaseModel):
    favorite: bool


class ScriptOut(ORMModel):
    id: int
    category: str
    title: str
    content: str
    tags: list | None = None
    is_favorite: bool = False
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


# ---------- 黑名单 ----------
class BlacklistCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str | None = Field(default=None, max_length=200)
    issue_type: str | None = Field(default=None, max_length=50)
    detail: str | None = None
    source: str | None = Field(default=None, max_length=200)


class BlacklistUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = None
    issue_type: str | None = None
    detail: str | None = None
    source: str | None = None


class BlacklistOut(ORMModel):
    id: int
    company: str
    position: str | None = None
    issue_type: str | None = None
    detail: str | None = None
    source: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 任务 ----------
class TaskCreate(BaseModel):
    task_type: str = Field(min_length=1, max_length=30)
    ref_id: int | None = None
    ref_type: str | None = Field(default=None, max_length=30)
    title: str = Field(min_length=1, max_length=300)
    due_date: date


class TaskUpdate(BaseModel):
    task_type: str | None = Field(default=None, min_length=1, max_length=30)
    ref_id: int | None = None
    ref_type: str | None = Field(default=None, max_length=30)
    title: str | None = Field(default=None, min_length=1, max_length=300)
    due_date: date | None = None


class TaskDoneIn(BaseModel):
    done: bool


class TaskOut(ORMModel):
    id: int
    task_type: str
    ref_id: int | None = None
    ref_type: str | None = None
    title: str
    due_date: date
    done: bool = False
    done_at: datetime | None = None
    created_at: datetime
    updated_at: datetime