"""
数据库引擎 & 会话工厂
使用 SQLAlchemy 2.0 异步引擎，支持 SQLite / PostgreSQL 切换。
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# 会话工厂 —— 每个请求通过依赖注入获取独立 session
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """所有模型继承的基类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖：获取数据库会话，请求结束后自动关闭"""
    async with async_session_factory() as session:
        yield session


async def init_db():
    """
    初始化数据库：创建所有表 & 插入默认管理员。
    在应用启动时调用。
    """
    import app.models  # noqa: F401 — 导入所有模型以注册到 Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建默认管理员
    from app.services.auth import create_admin_if_not_exists
    async with async_session_factory() as session:
        await create_admin_if_not_exists(session)
        await session.commit()
