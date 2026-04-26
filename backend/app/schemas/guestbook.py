"""
留言板模块请求/响应 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field


class GuestbookReply(BaseModel):
    """回复输出"""
    id: int
    content: str
    nickname: str
    website: str | None = None
    is_admin_reply: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GuestbookMessageOut(BaseModel):
    """留言输出（含回复列表）"""
    id: int
    content: str
    nickname: str
    website: str | None = None
    is_admin_reply: bool
    is_approved: bool
    replies: list[GuestbookReply] = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate_custom(cls, obj):
        """自定义验证：确保 replies 为列表"""
        data = {
            "id": obj.id,
            "content": obj.content,
            "nickname": obj.nickname,
            "website": obj.website,
            "is_admin_reply": obj.is_admin_reply,
            "is_approved": obj.is_approved,
            "replies": obj.replies or [],
            "created_at": obj.created_at,
        }
        return cls(**data)


class GuestbookCreate(BaseModel):
    """创建留言"""
    content: str = Field(..., min_length=1, max_length=5000, description="留言内容")
    nickname: str = Field(default="匿名", max_length=50, description="昵称")
    email: str | None = Field(None, max_length=200, description="邮箱")
    website: str | None = Field(None, max_length=500, description="个人网站")
    parent_id: int | None = Field(None, description="回复的目标留言 ID")


class GuestbookReview(BaseModel):
    """审核留言"""
    is_approved: bool = True
