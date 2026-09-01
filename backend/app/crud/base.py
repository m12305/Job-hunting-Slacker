"""通用数据访问助手。"""
from __future__ import annotations

from typing import TypeVar

from sqlalchemy.orm import Session

from ..core.errors import AppError

ModelT = TypeVar("ModelT")


def get_or_404(db: Session, model: type[ModelT], obj_id: int, label: str = "资源") -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise AppError(40400, f"{label}不存在或已被删除", 404)
    return obj