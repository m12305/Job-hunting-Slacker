"""投递状态机服务。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ..core.constants import APPLICATION_CLOSE_REASONS, STATUS_TRANSITIONS
from ..core.errors import AppError
from ..models import Application, ApplicationStatusLog


def change_status(
    db: Session,
    application: Application,
    to_status: str,
    note: str | None = None,
    close_reason: str | None = None,
) -> bool:
    """按状态转移表变更投递状态，并写入流水。返回是否发生了变更。"""
    if to_status not in STATUS_TRANSITIONS:
        raise AppError(40000, f"未知的投递状态：{to_status}")
    if close_reason and close_reason not in APPLICATION_CLOSE_REASONS:
        raise AppError(40000, f"未知的结束原因：{close_reason}")

    current = application.status
    if to_status == current:
        return False  # 幂等：状态未变化不写流水

    allowed = STATUS_TRANSITIONS.get(current, [])
    if to_status not in allowed:
        raise AppError(
            40900, f"非法状态流转：{current} -> {to_status}（允许：{', '.join(allowed) or '终态'}）", 409
        )

    effective_reason = close_reason
    if to_status == "resume_rejected":
        effective_reason = "resume_rejected"
    elif to_status == "rejected":
        effective_reason = "offer_declined"
    elif to_status == "ended":
        effective_reason = effective_reason or application.close_reason or "other"

    application.status = to_status
    if to_status in {"resume_rejected", "ended", "rejected"}:
        application.close_reason = effective_reason
        application.closed_at = datetime.now()
    else:
        application.close_reason = None
        application.closed_at = None
    db.add(
        ApplicationStatusLog(
            application_id=application.id,
            from_status=current,
            to_status=to_status,
            close_reason=effective_reason,
            note=note,
            changed_at=datetime.now(),
        )
    )
    return True
