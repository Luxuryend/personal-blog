"""
文件分享模块请求/响应 Schema
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ShareItemOut(BaseModel):
    """分享文件输出（列表用）"""
    id: int
    original_name: str
    stored_path: str
    file_size: int
    file_type: str | None = None
    is_image: bool
    has_extract_code: bool = False
    expires_at: datetime | None = None
    max_downloads: int | None = None
    download_count: int = 0
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_compat(cls, obj):
        """兼容 SQLAlchemy 模型转换"""
        return cls(
            id=obj.id,
            original_name=obj.original_name,
            stored_path=obj.stored_path,
            file_size=obj.file_size,
            file_type=obj.file_type,
            is_image=obj.is_image,
            has_extract_code=bool(obj.extract_code),
            expires_at=obj.expires_at,
            max_downloads=obj.max_downloads,
            download_count=obj.download_count,
            is_active=obj.is_active,
            created_at=obj.created_at,
        )


class ShareDetailOut(ShareItemOut):
    """分享文件详情（含提取码）"""
    extract_code: str | None = None
    stored_path: str

    model_config = {"from_attributes": True}


class ShareCreate(BaseModel):
    """创建分享"""
    extract_code: str | None = Field(None, min_length=4, max_length=10, description="提取码")
    expires_at: datetime | None = None
    max_downloads: int | None = Field(None, ge=1, description="最大下载次数")


class ShareAccessLogOut(BaseModel):
    """访问日志输出"""
    id: int
    share_id: int
    ip_address: str | None = None
    action: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractCodeRequest(BaseModel):
    """验证提取码"""
    extract_code: str = Field(..., min_length=1, max_length=10)


class ShareUpdate(BaseModel):
    """更新分享设置"""
    extract_code: str | None = Field(None, min_length=4, max_length=10, description="提取码，空字符串表示清除")
    expires_at: datetime | None = None
    max_downloads: int | None = Field(None, ge=1, description="最大下载次数，0 表示不限制")
    is_active: bool | None = None
