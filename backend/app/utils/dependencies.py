"""
FastAPI 依赖注入：鉴权、当前用户等
"""

from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth import AuthService
from app.models.user import User, UserRole

# HTTP Bearer Token 提取器
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    依赖：从 JWT 中解析当前用户。
    若 Token 无效或缺失则抛出 401。
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录或 Token 已过期")

    token = credentials.credentials
    user = await AuthService.verify_token(db, token)
    if user is None:
        raise HTTPException(status_code=401, detail="未登录或 Token 已过期")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    依赖：可选地从 JWT 中解析当前用户。
    未登录或 Token 无效时返回 None，不抛出异常。
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user = await AuthService.verify_token(db, token)
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    依赖：要求当前用户是管理员。
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="权限不足")
    return current_user
