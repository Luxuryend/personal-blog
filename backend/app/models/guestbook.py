"""
留言板模型
支持二级评论（回复功能），通过 parent_id 实现。
"""

from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GuestbookMessage(Base):
    """留言 / 回复"""
    __tablename__ = "guestbook_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="留言内容（过滤后存储）")
    nickname: Mapped[str] = mapped_column(String(50), default="匿名", comment="访客昵称")
    email: Mapped[str | None] = mapped_column(String(200), comment="邮箱（不公开）")
    website: Mapped[str | None] = mapped_column(String(500), comment="个人网站")

    # 二级评论
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("guestbook_messages.id"), comment="父留言 ID")
    is_admin_reply: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为管理员回复")

    # 审核 & 状态
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否通过审核")
    ip_address: Mapped[str | None] = mapped_column(String(50), comment="留言者 IP")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关联回复
    replies = relationship(
        "GuestbookMessage",
        backref="parent",
        remote_side=[id],
        lazy="selectin",
        order_by="GuestbookMessage.created_at",
    )
