"""
用户模型
区分管理员（ADMIN）与普通访客（VISITOR）。
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"       # 管理员（我）
    VISITOR = "visitor"   # 普通访客


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False, comment="密码哈希（bcrypt）")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.VISITOR, comment="角色")
    nickname: Mapped[str | None] = mapped_column(String(50), comment="昵称")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="更新时间")
