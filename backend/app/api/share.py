"""
文件分享 API
- 上传 & 创建分享（管理员）
- 浏览分享列表（访客可看已发布的分享）
- 验证提取码 & 下载文件
"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.share import ShareService
from app.schemas.share import ShareCreate, ShareUpdate, ShareItemOut, ShareDetailOut, ExtractCodeRequest, ShareAccessLogOut
from app.utils.response import ApiResponse
from app.utils.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/share", tags=["文件分享"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    extract_code: str | None = Query(None, min_length=4, max_length=10, description="提取码"),
    expires_at: str | None = Query(None, description="过期时间（ISO 格式）"),
    max_downloads: int | None = Query(None, ge=1, description="最大下载次数"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    上传文件并创建分享链接（管理员）。
    可选设置提取码、过期时间、下载次数限制。
    """
    from datetime import datetime
    share_config = ShareCreate(
        extract_code=extract_code,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        max_downloads=max_downloads,
    )
    try:
        share = await ShareService.create_share(db, file, admin.id, share_config)
        await db.commit()
        return ApiResponse.success(
            ShareDetailOut.model_validate(share).model_dump(),
            "文件上传成功",
        )
    except ValueError as e:
        return ApiResponse.bad_request(str(e))


@router.get("/files")
async def list_shares(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    浏览已公开的分享文件列表（访客可访问）。
    自动过滤已过期和已关闭的分享。
    """
    items, pagination = await ShareService.list_shares(db, page=page, page_size=page_size)

    # 过滤：仅返回有效且未过期的分享
    valid_items = []
    for item in items:
        if not item.is_active:
            continue
        if ShareService.is_expired(item):
            continue
        valid_items.append(ShareItemOut.from_orm_compat(item))

    return ApiResponse.success({
        "items": [i.model_dump() for i in valid_items],
        "pagination": pagination.model_dump(),
    })


@router.get("/files/admin")
async def list_all_shares_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """管理员查看所有分享（含已失效）"""
    items, pagination = await ShareService.list_shares(db, page=page, page_size=page_size, uploader_id=admin.id)
    return ApiResponse.success({
        "items": [ShareItemOut.from_orm_compat(i).model_dump() for i in items],
        "pagination": pagination.model_dump(),
    })


@router.get("/files/{share_id}")
async def get_share_detail(
    share_id: int,
    db: AsyncSession = Depends(get_db),
):
    """获取分享详情"""
    share = await ShareService.get_share_by_id(db, share_id)
    if share is None or not share.is_active:
        return ApiResponse.not_found("分享不存在或已失效")

    if ShareService.is_expired(share):
        return ApiResponse.bad_request("分享已过期")

    return ApiResponse.success(ShareDetailOut.model_validate(share).model_dump())


@router.post("/files/{share_id}/verify")
async def verify_extract_code(
    share_id: int,
    body: ExtractCodeRequest,
    db: AsyncSession = Depends(get_db),
):
    """验证提取码（下载前调用）"""
    share = await ShareService.get_share_by_id(db, share_id)
    if share is None or not share.is_active:
        return ApiResponse.not_found("分享不存在或已失效")

    if ShareService.is_expired(share):
        return ApiResponse.bad_request("分享已过期")

    if ShareService.is_download_limit_reached(share):
        return ApiResponse.bad_request("下载次数已达上限")

    if not ShareService.verify_extract_code(share, body.extract_code):
        return ApiResponse.bad_request("提取码错误")

    return ApiResponse.success(ShareDetailOut.model_validate(share).model_dump(), "验证通过")


@router.get("/files/{share_id}/download")
async def download_file(
    share_id: int,
    extract_code: str | None = Query(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    下载文件
    - 上传时未设置提取码则直接下载
    - 设置了提取码需先调用 verify 接口验证
    """
    share = await ShareService.get_share_by_id(db, share_id)
    if share is None or not share.is_active:
        return ApiResponse.not_found("分享不存在或已失效")

    if ShareService.is_expired(share):
        return ApiResponse.bad_request("分享已过期")

    if ShareService.is_download_limit_reached(share):
        return ApiResponse.bad_request("下载次数已达上限")

    # 需要提取码的必须通过 verify 接口
    if share.extract_code:
        return ApiResponse.bad_request("该文件需提取码，请先调用 verify 接口验证")

    # 增加下载计数并记录日志
    await ShareService.increment_download_count(db, share)
    await ShareService.record_access(
        db, share_id,
        ip_address=request.client.host if request else None,
        action="download",
    )
    await db.commit()

    # 返回文件（通过静态文件服务或重定向）
    from app.services.storage import storage
    from fastapi.responses import RedirectResponse
    file_url = storage.get_url(share.stored_path)
    return RedirectResponse(url=file_url)


@router.put("/files/{share_id}")
async def update_share(
    share_id: int,
    data: ShareUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    更新分享设置（管理员）
    可修改：提取码、过期时间、下载次数、启用状态
    """
    share = await ShareService.get_share_by_id(db, share_id)
    if share is None:
        return ApiResponse.not_found("分享不存在")

    share = await ShareService.update_share(db, share, data.model_dump(exclude_unset=True))
    await db.commit()
    return ApiResponse.success(ShareDetailOut.model_validate(share).model_dump(), "分享已更新")


@router.delete("/files/{share_id}")
async def delete_share(
    share_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除分享（管理员）"""
    share = await ShareService.get_share_by_id(db, share_id)
    if share is None:
        return ApiResponse.not_found("分享不存在")
    await ShareService.delete_share(db, share)
    await db.commit()
    return ApiResponse.success(message="分享已删除")


@router.get("/files/{share_id}/logs")
async def get_access_logs(
    share_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """查看分享的访问日志（管理员）"""
    items, pagination = await ShareService.get_access_logs(db, share_id, page, page_size)
    return ApiResponse.success({
        "items": [ShareAccessLogOut.model_validate(i).model_dump() for i in items],
        "pagination": pagination.model_dump(),
    })
