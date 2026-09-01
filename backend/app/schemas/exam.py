"""模块三：笔试 / 面试 / 题库。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .common import ORMModel


# ---------- 笔试 ----------
class ExamCreate(BaseModel):
    application_id: int | None = None
    exam_time: datetime | None = None
    platform: str | None = Field(default=None, max_length=50)
    exam_link: str | None = Field(default=None, max_length=500)
    account: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, max_length=200)
    duration_minutes: int | None = None
    status: str | None = Field(default=None, pattern="^(upcoming|done|cancelled)$")


class ExamUpdate(ExamCreate):
    pass


class ExamOut(ORMModel):
    id: int
    application_id: int | None = None
    exam_time: datetime | None = None
    platform: str | None = None
    exam_link: str | None = None
    account: str | None = None
    password: str | None = None
    duration_minutes: int | None = None
    status: str = "upcoming"
    created_at: datetime
    updated_at: datetime


class ExamReviewIn(BaseModel):
    passed: bool | None = None
    score: str | None = Field(default=None, max_length=100)
    questions: str | None = None
    wrong_questions: str | None = None
    key_points: list[str] | None = None
    summary: str | None = None


class ExamReviewOut(ORMModel):
    id: int
    exam_id: int
    passed: bool | None = None
    score: str | None = None
    questions: str | None = None
    wrong_questions: str | None = None
    key_points: list | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 面试 ----------
class InterviewCreate(BaseModel):
    application_id: int | None = None
    round: str | None = Field(default=None, max_length=20)
    interview_time: datetime | None = None
    interview_link: str | None = Field(default=None, max_length=500)
    self_intro: str | None = None
    prep_checklist: list | None = None
    status: str | None = Field(default=None, pattern="^(upcoming|done|cancelled)$")


class InterviewUpdate(InterviewCreate):
    pass


class InterviewOut(ORMModel):
    id: int
    application_id: int | None = None
    round: str | None = None
    interview_time: datetime | None = None
    interview_link: str | None = None
    self_intro: str | None = None
    prep_checklist: list | None = None
    status: str = "upcoming"
    created_at: datetime
    updated_at: datetime


class InterviewQaCreate(BaseModel):
    question: str = Field(min_length=1)
    my_answer: str | None = None
    feedback: str | None = None
    category: str | None = Field(default=None, max_length=30)


class InterviewQaUpdate(BaseModel):
    question: str | None = Field(default=None, min_length=1)
    my_answer: str | None = None
    feedback: str | None = None
    category: str | None = Field(default=None, max_length=30)


class InterviewQaOut(ORMModel):
    id: int
    interview_id: int
    question: str
    my_answer: str | None = None
    feedback: str | None = None
    category: str | None = None
    created_at: datetime


class InterviewResultIn(BaseModel):
    result: str = Field(pattern="^(passed|failed)$")
    fail_reason: str | None = None
    summary: str | None = None


class InterviewResultOut(ORMModel):
    id: int
    interview_id: int
    result: str | None = None
    fail_reason: str | None = None
    audio_path: str | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------- 题库 ----------
class QuestionCreate(BaseModel):
    category: str | None = Field(default=None, max_length=30)
    title: str = Field(min_length=1, max_length=300)
    difficulty: str | None = Field(default=None, max_length=20)
    content: str | None = None
    answer: str | None = None
    tags: list[str] | None = None
    source: str | None = Field(default=None, max_length=200)
    review_status: str | None = Field(default=None, pattern="^(new|todo|mastered)$")


class QuestionUpdate(BaseModel):
    category: str | None = Field(default=None, max_length=30)
    title: str | None = Field(default=None, min_length=1, max_length=300)
    difficulty: str | None = Field(default=None, max_length=20)
    content: str | None = None
    answer: str | None = None
    tags: list[str] | None = None
    source: str | None = Field(default=None, max_length=200)
    review_status: str | None = Field(default=None, pattern="^(new|todo|mastered)$")


class ReviewStatusIn(BaseModel):
    review_status: str = Field(pattern="^(new|todo|mastered)$")


class QuestionOut(ORMModel):
    id: int
    category: str | None = None
    title: str
    difficulty: str | None = None
    content: str | None = None
    answer: str | None = None
    tags: list | None = None
    source: str | None = None
    review_status: str = "new"
    created_at: datetime
    updated_at: datetime