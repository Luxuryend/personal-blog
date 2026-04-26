"""
通用分页 Schema
"""

from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class Pagination(BaseModel):
    """分页信息"""
    page: int
    page_size: int
    total: int
    total_pages: int


class PageResult(BaseModel, Generic[T]):
    """分页结果包装"""
    items: list[T]
    pagination: Pagination
