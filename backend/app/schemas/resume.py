"""模块一：岗位类型 / 简历 / 修改日志 / 素材 / 资产。"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from .common import ORMModel


# ---------- 岗位类型 ----------
class JobTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    sort_order: int = 0


class JobTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = None
    sort_order: int | None = None


class JobTypeOut(ORMModel):
    id: int
    name: str
    color: str | None = None
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


# ---------- 简历版本 ----------
class ResumeCreate(BaseModel):
    job_type_id: int | None = None
    version_name: str = Field(min_length=1, max_length=100)
    target_position: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, pattern="^(draft|active|archived)$")
    is_default: bool = False
    remark: str | None = None


class ResumeUpdate(BaseModel):
    job_type_id: int | None = None
    version_name: str | None = Field(default=None, min_length=1, max_length=100)
    target_position: str | None = None
    status: str | None = Field(default=None, pattern="^(draft|active|archived)$")
    is_default: bool | None = None
    remark: str | None = None


class ResumeOut(ORMModel):
    id: int
    job_type_id: int | None = None
    job_type_name: str | None = None
    version_name: str
    target_position: str | None = None
    file_path: str | None = None
    file_name: str | None = None
    file_type: str | None = None
    file_size: int | None = None
    status: str = "active"
    is_default: bool = False
    remark: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 修改日志 ----------
class ResumeLogCreate(BaseModel):
    resume_version_id: int
    change_desc: str = Field(min_length=1)
    changed_at: datetime | None = None


class ResumeLogOut(ORMModel):
    id: int
    resume_version_id: int
    change_desc: str
    changed_at: datetime
    trigger_source: str = "manual"


# ---------- 素材库 ----------
class MaterialCreate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    organization: str | None = Field(default=None, max_length=200)
    role: str | None = Field(default=None, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    highlights: str | None = None
    tech_stack: list[str] | None = None
    attachments: list[str] | None = None
    tags: list[str] | None = None


class MaterialUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    organization: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    highlights: str | None = None
    tech_stack: list[str] | None = None
    attachments: list[str] | None = None
    tags: list[str] | None = None


class MaterialOut(ORMModel):
    id: int
    category: str
    title: str
    organization: str | None = None
    role: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    highlights: str | None = None
    tech_stack: list | None = None
    attachments: list | None = None
    tags: list | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 资产归档 ----------
class AssetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=500)
    file_path: str | None = Field(default=None, max_length=500)
    description: str | None = None
    tags: list[str] | None = None


class AssetUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    url: str | None = None
    file_path: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class AssetOut(ORMModel):
    id: int
    category: str
    title: str
    url: str | None = None
    file_path: str | None = None
    description: str | None = None
    tags: list | None = None
    created_at: datetime
    updated_at: datetime