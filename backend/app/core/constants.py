"""枚举常量与业务常量（与《数据库设计》《API 接口契约》保持一致）。

枚举统一为小写下划线字符串，前端负责映射中文展示。
"""

# ---- 模块一 ----
RESUME_STATUS = ["draft", "active", "archived"]
RESUME_FILE_TYPES = ["pdf", "doc", "docx"]
MATERIAL_CATEGORIES = ["project", "internship", "campus", "award", "other"]
ASSET_CATEGORIES = ["blog", "project", "github", "transcript", "certificate", "other"]

# ---- 模块二 ----
APPLICATION_STATUS = [
    "pending", "applied", "resume_screening", "resume_rejected",
    "exam", "interview", "ended", "offered", "rejected",
]
APPLICATION_CHANNELS = ["boss", "nowcoder", "official", "referral", "other"]
APPLICATION_CLOSE_REASONS = [
    "resume_rejected",
    "exam_failed",
    "employer_rejected",
    "offer_declined",
    "withdrew",
    "hiring_frozen",
    "position_closed",
    "no_response",
    "other",
]
OFFER_STATUS = ["pending", "accepted", "rejected"]
# 内置 Offer 打分维度
OFFER_DIMENSIONS = [
    ("salary", "薪资"),
    ("city", "城市"),
    ("work_intensity", "加班强度"),
    ("industry", "行业前景"),
    ("company_scale", "公司规模"),
    ("position_dev", "岗位发展"),
]

# 投递状态机：状态 -> 合法可流转去向（《技术架构与设计》4.1）
STATUS_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["applied", "ended"],
    "applied": ["resume_screening", "resume_rejected", "exam", "interview", "ended"],
    "resume_screening": ["resume_rejected", "exam", "interview", "ended"],
    "resume_rejected": ["ended"],
    "exam": ["interview", "ended"],
    "interview": ["ended", "offered"],
    "ended": ["offered"],
    "offered": ["rejected"],
    "rejected": [],
}

# ---- 模块三 ----
INTERVIEW_ROUNDS = ["first", "second", "third", "hr", "final", "other"]
EXAM_PLATFORMS = ["nowcoder", "saikr", "official", "other"]
EXAM_STATUS = ["upcoming", "done", "cancelled"]
INTERVIEW_STATUS = ["upcoming", "done", "cancelled"]
INTERVIEW_RESULTS = ["passed", "failed"]
QUESTION_CATEGORIES = ["code", "baguwen", "project_ask", "other"]
QUESTION_DIFFICULTY = ["easy", "medium", "hard"]
QUESTION_REVIEW_STATUS = ["new", "todo", "mastered"]

# ---- 模块五 ----
SCRIPT_CATEGORIES = ["general", "tech", "custom"]
BLACKLIST_TYPES = ["overtime", "fake_salary", "free_trial", "trap_interview", "other"]
TASK_TYPES = ["apply", "review", "coding", "custom"]
TASK_REF_TYPES = ["application", "exam", "question"]
