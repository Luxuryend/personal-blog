"""
文件/图片分享模块模型
支持提取码、有效期、访问日志。
"""

from datetime import datetime
from sqlalchemy import String, Integer, Boolean, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShareItem(Base):
    """分享文件记录"""
    __tablename__ = "share_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 文件信息
    original_name: Mapped[str] = mapped_column(String(500), nullable=False, comment="原始文件名")
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False, comment="存储路径（相对 upload_dir）")
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, comment="文件大小（字节）")
    file_type: Mapped[str] = mapped_column(String(100), comment="MIME 类型")
    is_image: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为图片")

    # 分享控制
    extract_code: Mapped[str | None] = mapped_column(String(10), comment="提取码（为空则无需提取码）")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, comment="过期时间（为空则永不过期）")
    max_downloads: Mapped[int | None] = mapped_column(Integer, comment="最大下载次数限制")
    download_count: Mapped[int] = mapped_column(Integer, default=0, comment="已下载次数")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否有效（可手动关闭）")

    # 上传者
    uploader_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class ShareAccessLog(Base):
    """分享文件访问日志"""
    __tablename__ = "share_access_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    share_id: Mapped[int] = mapped_column(Integer, ForeignKey("share_items.id", ondelete="CASCADE"), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(50), comment="访问者 IP")
    user_agent: Mapped[str | None] = mapped_column(Text, comment="User-Agent")
    action: Mapped[str] = mapped_column(String(20), default="download", comment="访问类型: view / download")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
