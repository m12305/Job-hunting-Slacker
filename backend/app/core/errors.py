"""业务异常与全局异常处理。

错误码约定（《API 接口契约》第 8 节）：
    0     成功
    40000 参数校验失败
    40400 资源不存在
    40900 冲突（有关联删除 / 非法状态流转）
    50000 服务器错误
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("qiuzhao-room")


class AppError(Exception):
    """业务错误，携带业务 code、展示 message 与 HTTP 状态码。"""

    def __init__(self, code: int, message: str, http_status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status


def fail(code: int, message: str, data=None) -> dict:
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        return JSONResponse(status_code=exc.http_status, content=fail(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError):
        first = exc.errors()[0] if exc.errors() else {}
        loc = ".".join(str(x) for x in first.get("loc", [])) or "param"
        msg = first.get("msg", "参数校验失败")
        return JSONResponse(status_code=400, content=fail(40000, f"{loc}: {msg}"))

    @app.exception_handler(IntegrityError)
    async def integrity_handler(_request: Request, exc: IntegrityError):
        logger.warning("IntegrityError: %s", exc)
        return JSONResponse(
            status_code=409,
            content=fail(40900, "数据冲突：可能存在关联数据或重复值，请检查后重试"),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(status_code=500, content=fail(50000, "服务器内部错误"))
