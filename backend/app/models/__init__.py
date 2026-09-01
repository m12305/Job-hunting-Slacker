"""全部模型的汇总入口（保证 Base.metadata 注册完整）。"""
from .base import Base
from .resume import Asset, JobType, Material, Resume, ResumeLog
from .application import Application, ApplicationStatusLog, Offer, OfferWeightConfig
from .exam import Exam, ExamReview, Interview, InterviewQa, InterviewResult, Question
from .misc import Blacklist, Script, Setting, Task

__all__ = [
    "Base",
    "JobType", "Resume", "ResumeLog", "Material", "Asset",
    "Application", "ApplicationStatusLog", "Offer", "OfferWeightConfig",
    "Exam", "ExamReview", "Interview", "InterviewQa", "InterviewResult", "Question",
    "Script", "Blacklist", "Task", "Setting",
]