"""
统一 API 响应格式
所有接口返回 {"code": 0, "data": ..., "message": "ok"}
"""

from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class ApiResponse:
    """
    统一响应体
    code: 0 表示成功，非 0 表示错误码
    data: 实际数据（可以是 dict / list / None）
    message: 描述信息
    """

    @staticmethod
    def success(data: Any = None, message: str = "ok") -> JSONResponse:
        return JSONResponse(content=jsonable_encoder({
            "code": 0,
            "data": data,
            "message": message,
        }))

    @staticmethod
    def error(code: int = 400, message: str = "error", data: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=200,  # 业务状态通过 code 表达，HTTP 统一 200
            content=jsonable_encoder({
                "code": code,
                "data": data,
                "message": message,
            })
        )

    # ── 常用快捷方法 ────────────────────────────────────────
    bad_request = lambda msg="请求参数错误": ApiResponse.error(400, msg)  # noqa: E731
    unauthorized = lambda msg="未登录或 Token 已过期": ApiResponse.error(401, msg)  # noqa: E731
    forbidden = lambda msg="权限不足": ApiResponse.error(403, msg)  # noqa: E731
    not_found = lambda msg="资源不存在": ApiResponse.error(404, msg)  # noqa: E731
