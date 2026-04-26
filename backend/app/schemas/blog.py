"""
博客模块请求/响应 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field


class BlogCategoryOut(BaseModel):
    """分类输出"""
    id: int
    name: str
    slug: str
    description: str | None = None

    model_config = {"from_attributes": True}


class BlogTagOut(BaseModel):
    """标签输出"""
    id: int
    name: str

    model_config = {"from_attributes": True}


class BlogSummary(BaseModel):
    """文章列表摘要"""
    id: int
    title: str
    slug: str
    summary: str | None = None
    cover_image: str | None = None
    is_published: bool
    is_top: bool
    view_count: int
    category: BlogCategoryOut | None = None
    tags: list[BlogTagOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlogDetail(BaseModel):
    """文章详情（含正文）"""
    id: int
    title: str
    slug: str
    content: str
    summary: str | None = None
    cover_image: str | None = None
    is_published: bool
    is_top: bool
    view_count: int
    category: BlogCategoryOut | None = None
    tags: list[BlogTagOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlogCreate(BaseModel):
    """创建文章"""
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200, pattern=r"^[a-z0-9\-]+$")
    content: str = Field(..., min_length=1)
    summary: str | None = Field(None, max_length=500)
    cover_image: str | None = None
    is_published: bool = False
    is_top: bool = False
    category_id: int | None = None
    tag_ids: list[int] = []


class BlogUpdate(BaseModel):
    """更新文章"""
    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200, pattern=r"^[a-z0-9\-]+$")
    content: str | None = Field(None, min_length=1)
    summary: str | None = Field(None, max_length=500)
    cover_image: str | None = None
    is_published: bool | None = None
    is_top: bool | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9\-]+$")
    description: str | None = Field(None, max_length=200)


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
