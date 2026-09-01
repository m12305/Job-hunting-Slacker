"""模块三：笔试 / 面试 / 题库。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Exam(Base, TimestampMixin):
    """笔试记录（5.1）。"""

    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    exam_time: Mapped[datetime | None] = mapped_column(DateTime)
    platform: Mapped[str | None] = mapped_column(String(50))
    exam_link: Mapped[str | None] = mapped_column(String(500))
    account: Mapped[str | None] = mapped_column(String(100))
    password: Mapped[str | None] = mapped_column(String(200))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="upcoming", nullable=False)


class ExamReview(Base, TimestampMixin):
    """笔试复盘（5.2，1:1）。"""

    __tablename__ = "exam_reviews"
    __table_args__ = (UniqueConstraint("exam_id", name="uq_exam_review_exam_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"), index=True, nullable=False
    )
    passed: Mapped[bool | None] = mapped_column(Boolean)
    score: Mapped[str | None] = mapped_column(String(100))
    questions: Mapped[str | None] = mapped_column(Text)
    wrong_questions: Mapped[str | None] = mapped_column(Text)
    key_points: Mapped[list | None] = mapped_column(JSON, default=list)
    summary: Mapped[str | None] = mapped_column(Text)


class Interview(Base, TimestampMixin):
    """面试记录（5.3）。"""

    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    round: Mapped[str | None] = mapped_column(String(20))
    interview_time: Mapped[datetime | None] = mapped_column(DateTime)
    interview_link: Mapped[str | None] = mapped_column(String(500))
    self_intro: Mapped[str | None] = mapped_column(Text)
    prep_checklist: Mapped[list | None] = mapped_column(JSON, default=list)  # [{label,done}]
    status: Mapped[str] = mapped_column(String(20), default="upcoming", nullable=False)


class InterviewQa(Base):
    """面试问答复盘（5.4）。"""

    __tablename__ = "interview_qa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    my_answer: Mapped[str | None] = mapped_column(Text)
    feedback: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class InterviewResult(Base, TimestampMixin):
    """面试结果（5.5，1:1）。"""

    __tablename__ = "interview_results"
    __table_args__ = (UniqueConstraint("interview_id", name="uq_interview_result_interview_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # 注：设计稿为 NOT NULL，但允许先上传录音再补结果，故放开为可空
    result: Mapped[str | None] = mapped_column(String(20))
    fail_reason: Mapped[str | None] = mapped_column(Text)
    audio_path: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)


class Question(Base, TimestampMixin):
    """题库题目（5.6）。"""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str | None] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str | None] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    source: Mapped[str | None] = mapped_column(String(200))
    review_status: Mapped[str] = mapped_column(String(20), default="new", index=True, nullable=False)