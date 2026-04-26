"""
认证服务
提供 JWT 签发 / 验证、密码哈希、管理员初始化。
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User, UserRole

# bcrypt 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证相关业务逻辑"""

    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行 bcrypt 哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """校验明文密码与哈希值是否匹配"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        """
        签发 JWT Token
        payload 包含 user_id 和 role，过期时间取自配置。
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    async def verify_token(db: AsyncSession, token: str) -> User | None:
        """
        验证 JWT Token，返回对应用户对象。
        若 Token 无效或用户不存在则返回 None。
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = int(payload.get("sub"))
        except (JWTError, ValueError, TypeError):
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
        """
        用户名密码认证。成功返回 User，失败返回 None。
        管理员密码直接从 settings.ADMIN_PASSWORD 校验，不依赖数据库哈希。
        """
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            return None
        if user.role == UserRole.ADMIN:
            if password != settings.ADMIN_PASSWORD:
                return None
        else:
            if not AuthService.verify_password(password, user.password_hash):
                return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, username: str, password: str, nickname: str | None = None, role: UserRole = UserRole.VISITOR) -> User:
        """创建新用户"""
        user = User(
            username=username,
            password_hash=AuthService.hash_password(password),
            nickname=nickname or username,
            role=role,
        )
        db.add(user)
        await db.flush()
        return user


async def create_admin_if_not_exists(db: AsyncSession):
    """
    初始化管理员账户（幂等）。
    在首次启动数据库时调用。
    """
    result = await db.execute(select(User).where(User.role == UserRole.ADMIN))
    admin = result.scalar_one_or_none()
    if admin is None:
        admin = User(
            username=settings.ADMIN_USERNAME,
            password_hash=AuthService.hash_password(settings.ADMIN_PASSWORD),
            nickname="管理员",
            role=UserRole.ADMIN,
        )
        db.add(admin)
