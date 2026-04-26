"""
文件分享服务
处理文件上传、分享链接管理、提取码验证、访问日志等。
"""

import os
import string
import random
from datetime import datetime, timezone
from math import ceil

from fastapi import UploadFile
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import ShareItem, ShareAccessLog
from app.schemas.share import ShareCreate
from app.schemas.common import Pagination
from app.services.storage import storage


def _generate_extract_code(length: int = 6) -> str:
    """生成随机提取码（数字 + 大写字母）"""
    chars = string.digits + string.ascii_uppercase
    return "".join(random.choices(chars, k=length))


# 允许的图片 MIME 类型
IMAGE_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "image/bmp", "image/svg+xml",
}

# 允许的文件 MIME 类型前缀
ALLOWED_MIME_PREFIXES = {
    "image/", "text/", "application/pdf",
    "application/zip", "application/x-rar-compressed",
    "application/x-7z-compressed", "application/json",
    "application/msword", "application/vnd.openxmlformats-officedocument",
    "application/vnd.ms-excel", "application/vnd.ms-powerpoint",
}


def is_allowed_file_type(mime_type: str) -> bool:
    """校验文件 MIME 类型是否允许上传"""
    if mime_type in IMAGE_MIME_TYPES:
        return True
    for prefix in ALLOWED_MIME_PREFIXES:
        if mime_type.startswith(prefix):
            return True
    return False


class ShareService:
    """分享业务逻辑"""

    @staticmethod
    async def create_share(
        db: AsyncSession,
        file: UploadFile,
        uploader_id: int,
        share_config: ShareCreate | None = None,
    ) -> ShareItem:
        """
        上传文件并创建分享记录。
        - 校验文件类型
        - 存储文件（本地或 OSS）
        - 写入数据库
        """
        # 校验 MIME 类型
        mime_type = file.content_type or "application/octet-stream"
        if not is_allowed_file_type(mime_type):
            raise ValueError(f"不支持的文件类型: {mime_type}")

        # 判断是否为图片
        is_image = mime_type in IMAGE_MIME_TYPES

        # 文件存储
        sub_dir = "images" if is_image else "docs"
        stored_path = await storage.save(file, sub_dir=sub_dir)

        # 提取码
        extract_code = None
        if share_config and share_config.extract_code:
            extract_code = share_config.extract_code
        elif share_config and share_config.extract_code is None:
            extract_code = None  # 明确不设置
        else:
            extract_code = None

        share = ShareItem(
            original_name=file.filename or "unnamed",
            stored_path=stored_path,
            file_size=file.size or 0,
            file_type=mime_type,
            is_image=is_image,
            extract_code=extract_code,
            expires_at=share_config.expires_at if share_config else None,
            max_downloads=share_config.max_downloads if share_config else None,
            uploader_id=uploader_id,
        )
        db.add(share)
        await db.flush()
        return share

    @staticmethod
    async def list_shares(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 12,
        uploader_id: int | None = None,
    ) -> tuple[list[ShareItem], Pagination]:
        """分页查询分享列表"""
        query = select(ShareItem)

        if uploader_id is not None:
            query = query.where(ShareItem.uploader_id == uploader_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(ShareItem.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if page_size > 0 else 0,
        )
        return items, pagination

    @staticmethod
    async def get_share_by_id(db: AsyncSession, share_id: int) -> ShareItem | None:
        """获取分享详情"""
        result = await db.execute(select(ShareItem).where(ShareItem.id == share_id))
        return result.scalar_one_or_none()

    @staticmethod
    def verify_extract_code(share: ShareItem, code: str) -> bool:
        """验证提取码（大小写不敏感）"""
        if not share.extract_code:
            return True  # 无需提取码
        return share.extract_code.upper() == code.upper()

    @staticmethod
    def is_expired(share: ShareItem) -> bool:
        """检查分享是否过期"""
        if share.expires_at is None:
            return False
        return datetime.now(timezone.utc).replace(tzinfo=None) > share.expires_at.replace(tzinfo=None) if share.expires_at.tzinfo is None else datetime.now(timezone.utc) > share.expires_at

    @staticmethod
    def is_download_limit_reached(share: ShareItem) -> bool:
        """检查下载次数是否已达上限"""
        if share.max_downloads is None:
            return False
        return share.download_count >= share.max_downloads

    @staticmethod
    async def record_access(
        db: AsyncSession,
        share_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None,
        action: str = "download",
    ):
        """记录访问日志"""
        log = ShareAccessLog(
            share_id=share_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
        )
        db.add(log)
        await db.flush()

    @staticmethod
    async def increment_download_count(db: AsyncSession, share: ShareItem):
        """增加下载计数"""
        share.download_count += 1
        await db.flush()

    @staticmethod
    async def delete_share(db: AsyncSession, share: ShareItem):
        """删除分享（同时删除文件）"""
        # 删除存储的文件
        await storage.delete(share.stored_path)
        # 删除数据库记录
        await db.delete(share)
        await db.flush()

    @staticmethod
    async def update_share(db: AsyncSession, share: ShareItem, update_data: dict) -> ShareItem:
        """更新分享设置"""
        from datetime import datetime

        for field, value in update_data.items():
            if value is None:
                continue
            if field == "extract_code" and value == "":
                setattr(share, field, None)
            elif field == "max_downloads" and value == 0:
                setattr(share, field, None)
            else:
                setattr(share, field, value)

        share.updated_at = datetime.now()
        await db.flush()
        return share

    @staticmethod
    async def get_access_logs(
        db: AsyncSession,
        share_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ShareAccessLog], Pagination]:
        """获取分享的访问日志"""
        query = select(ShareAccessLog).where(ShareAccessLog.share_id == share_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(ShareAccessLog.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if page_size > 0 else 0,
        )
        return items, pagination
