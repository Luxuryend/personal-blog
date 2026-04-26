"""
文件存储服务
提供本地存储与对象存储（OSS）的抽象接口，可轻松切换。
目前实现本地存储，OSS 模块预留。
"""

import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile

from app.config import settings


class StorageBackend:
    """存储后端基类 / 接口定义"""

    async def save(self, file: UploadFile, sub_dir: str = "") -> str:
        """
        保存文件，返回存储路径（相对路径）。
        子类需实现此方法。
        """
        raise NotImplementedError

    async def delete(self, relative_path: str):
        """删除文件"""
        raise NotImplementedError

    def get_url(self, relative_path: str) -> str:
        """获取文件访问 URL"""
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """本地文件存储"""

    def __init__(self):
        self._upload_dir = Path(settings.UPLOAD_DIR)
        self._upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, sub_dir: str = "") -> str:
        """
        保存上传文件到本地。
        - sub_dir: 子目录名（如 "images", "docs"）
        - 返回相对路径：sub_dir/unique_filename.ext
        """
        # 生成唯一文件名
        ext = ""
        if file.filename and "." in file.filename:
            ext = file.filename.rsplit(".", 1)[-1].lower()

        unique_name = f"{uuid.uuid4().hex}{'.' + ext if ext else ''}"

        # 目标目录
        target_dir = self._upload_dir / sub_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / unique_name

        # 写入文件
        content = await file.read()
        async with aiofiles.open(str(target_path), "wb") as f:
            await f.write(content)

        relative = os.path.join(sub_dir, unique_name).replace("\\", "/")
        return relative

    async def delete(self, relative_path: str):
        """删除本地文件"""
        full_path = self._upload_dir / relative_path
        if full_path.exists():
            os.remove(str(full_path))

    def get_url(self, relative_path: str) -> str:
        """返回文件访问路径（通过后端静态文件服务）"""
        return f"/uploads/{relative_path}"


class OSSStorage(StorageBackend):
    """对象存储（预留）"""

    async def save(self, file: UploadFile, sub_dir: str = "") -> str:
        # TODO: 使用 boto3 / oss2 SDK 上传
        raise NotImplementedError("OSS 存储尚未实现")

    async def delete(self, relative_path: str):
        raise NotImplementedError("OSS 存储尚未实现")

    def get_url(self, relative_path: str) -> str:
        # TODO: 返回 OSS 签名 URL 或 CDN URL
        return f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}/{relative_path}"


# ── 工厂函数 ────────────────────────────────────────────────

def get_storage_backend() -> StorageBackend:
    """根据配置返回对应的存储后端实例"""
    if settings.STORAGE_BACKEND == "oss":
        return OSSStorage()
    return LocalStorage()


# 全局存储后端实例
storage = get_storage_backend()
