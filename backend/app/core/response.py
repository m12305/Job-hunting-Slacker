"""统一响应封装。"""
from __future__ import annotations

from typing import Any


def ok(data: Any = None) -> dict:
    """成功响应：{code:0, message:"ok", data}"""
    return {"code": 0, "message": "ok", "data": data}


def page_data(items: list, total: int, page: int, page_size: int) -> dict:
    """分页数据体。"""
    return {"items": items, "total": total, "page": page, "page_size": page_size}