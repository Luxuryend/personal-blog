"""
全局配置模块
从 .env 或环境变量中读取配置，Pydantic 自动校验类型。
"""

from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    # ── 数据库 ──────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./personal_website.db"

    # ── JWT ─────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 小时

    # ── 管理员初始化 ─────────────────────────────────────────
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123456"

    # ── 文件存储 ────────────────────────────────────────────
    STORAGE_BACKEND: Literal["local", "oss"] = "local"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE_MB: int = 100

    # ── OSS（预留） ─────────────────────────────────────────
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET: str = ""
    OSS_ENDPOINT: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
