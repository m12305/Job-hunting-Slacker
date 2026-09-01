"""模块二：投递 / 状态流水 / Offer / 权重 / 对比。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import ORMModel


# ---------- 投递 ----------
class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    city: str | None = Field(default=None, max_length=100)
    salary_min: int | None = Field(default=None, ge=0, le=999)
    salary_max: int | None = Field(default=None, ge=0, le=999)
    salary_currency: str = "CNY"
    channel: str | None = Field(default=None, max_length=50)
    apply_time: datetime | None = None
    resume_version_id: int | None = None
    job_type_id: int | None = None
    status: str | None = Field(default=None, max_length=30)
    close_reason: str | None = Field(
        default=None,
        pattern="^(resume_rejected|exam_failed|employer_rejected|offer_declined|withdrew|hiring_frozen|position_closed|no_response|other)$",
    )
    source_url: str | None = Field(default=None, max_length=500)
    remark: str | None = None

    @field_validator("company", "position", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str | None):
        if value and urlparse(value).scheme.lower() not in {"http", "https"}:
            raise ValueError("链接仅支持 http 或 https")
        return value

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("薪资下限不能高于上限")
        return self


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, min_length=1, max_length=200)
    city: str | None = None
    salary_min: int | None = Field(default=None, ge=0, le=999)
    salary_max: int | None = Field(default=None, ge=0, le=999)
    salary_currency: str | None = None
    channel: str | None = None
    apply_time: datetime | None = None
    resume_version_id: int | None = None
    job_type_id: int | None = None
    source_url: str | None = Field(default=None, max_length=500)
    remark: str | None = None

    @field_validator("company", "position", mode="before")
    @classmethod
    def strip_optional_required_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, value: str | None):
        if value and urlparse(value).scheme.lower() not in {"http", "https"}:
            raise ValueError("链接仅支持 http 或 https")
        return value

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            raise ValueError("薪资下限不能高于上限")
        return self


class StatusChangeIn(BaseModel):
    to_status: str = Field(min_length=1, max_length=30)
    close_reason: str | None = Field(
        default=None,
        pattern="^(resume_rejected|exam_failed|employer_rejected|offer_declined|withdrew|hiring_frozen|position_closed|no_response|other)$",
    )
    note: str | None = None


class ApplicationOut(ORMModel):
    id: int
    company: str
    position: str
    city: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str = "CNY"
    channel: str | None = None
    apply_time: datetime | None = None
    resume_version_id: int | None = None
    resume_version_name: str | None = None
    job_type_id: int | None = None
    job_type_name: str | None = None
    status: str = "pending"
    close_reason: str | None = None
    closed_at: datetime | None = None
    source_url: str | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime


class StatusLogOut(ORMModel):
    id: int
    application_id: int
    from_status: str | None = None
    to_status: str
    close_reason: str | None = None
    note: str | None = None
    changed_at: datetime


class ApplicationDetailOut(ApplicationOut):
    timeline: list[StatusLogOut] = []
    exams: list[dict] = []
    interviews: list[dict] = []
    offers: list[dict] = []
    blacklist_hits: int = 0


# ---------- Offer ----------
class OfferCreate(BaseModel):
    application_id: int | None = None
    company: str = Field(min_length=1, max_length=200)
    position: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, max_length=100)
    salary_base: Decimal | None = None
    salary_months: int | None = None
    bonus_performance: Decimal | None = None
    signing_bonus: Decimal | None = None
    housing_fund: str | None = Field(default=None, max_length=100)
    stock_options: str | None = Field(default=None, max_length=200)
    work_intensity: int | None = Field(default=None, ge=1, le=5)
    industry_prospect: int | None = Field(default=None, ge=1, le=5)
    company_scale: str | None = Field(default=None, max_length=100)
    position_development: int | None = Field(default=None, ge=1, le=5)
    other_notes: str | None = None
    status: str | None = Field(default=None, pattern="^(pending|accepted|rejected)$")
    extra_scores: dict | None = None


class OfferUpdate(OfferCreate):
    company: str | None = Field(default=None, min_length=1, max_length=200)


class OfferOut(ORMModel):
    id: int
    application_id: int | None = None
    company: str
    position: str | None = None
    city: str | None = None
    salary_base: Decimal | None = None
    salary_months: int | None = None
    bonus_performance: Decimal | None = None
    signing_bonus: Decimal | None = None
    housing_fund: str | None = None
    stock_options: str | None = None
    work_intensity: int | None = None
    industry_prospect: int | None = None
    company_scale: str | None = None
    position_development: int | None = None
    other_notes: str | None = None
    status: str = "pending"
    extra_scores: dict | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 权重配置 ----------
class OfferWeightIn(BaseModel):
    dimension_key: str = Field(min_length=1, max_length=50)
    dimension_name: str = Field(min_length=1, max_length=50)
    weight: float = Field(ge=0)
    enabled: bool = True
    sort_order: int = 0


class OfferWeightOut(ORMModel):
    id: int
    dimension_key: str
    dimension_name: str
    weight: float
    enabled: bool
    sort_order: int


# ---------- 对比 ----------
class OfferCompareIn(BaseModel):
    offer_ids: list[int] = Field(min_length=1)
    weight_overrides: dict[str, object] | None = None
