"""模块二：投递记录 / 状态流水 / Offer / 权重配置。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Application(Base, TimestampMixin):
    """投递记录（4.1）。"""

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100))
    salary_min: Mapped[int | None] = mapped_column(Integer)  # 单位 K/月
    salary_max: Mapped[int | None] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(10), default="CNY", nullable=False)
    channel: Mapped[str | None] = mapped_column(String(50))
    apply_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    resume_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL")
    )
    job_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_types.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True, nullable=False)
    close_reason: Mapped[str | None] = mapped_column(String(40), index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500))
    remark: Mapped[str | None] = mapped_column(Text)


class ApplicationStatusLog(Base):
    """投递状态流水（4.2）。"""

    __tablename__ = "application_status_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    close_reason: Mapped[str | None] = mapped_column(String(40))
    note: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class Offer(Base, TimestampMixin):
    """Offer（4.3）。"""

    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    company: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    position: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    salary_base: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # 月 base（单位 K）
    salary_months: Mapped[int | None] = mapped_column(Integer)  # 发放月数
    bonus_performance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # 绩效奖金
    signing_bonus: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # 签字费
    housing_fund: Mapped[str | None] = mapped_column(String(100))  # 公积金说明
    stock_options: Mapped[str | None] = mapped_column(String(200))  # 股票/期权
    work_intensity: Mapped[int | None] = mapped_column(Integer)  # 1-5，越大越卷
    industry_prospect: Mapped[int | None] = mapped_column(Integer)  # 1-5
    company_scale: Mapped[str | None] = mapped_column(String(100))
    position_development: Mapped[int | None] = mapped_column(Integer)  # 1-5
    other_notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    # 扩展：自定义维度打分（dimension_key -> 0-100），供 custom_* 维度使用
    extra_scores: Mapped[dict | None] = mapped_column(JSON, default=dict)


class OfferWeightConfig(Base):
    """Offer 打分权重配置（4.4）。"""

    __tablename__ = "offer_weight_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dimension_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    dimension_name: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
