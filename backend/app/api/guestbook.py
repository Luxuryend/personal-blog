"""
留言板 API
- 访客：创建留言/回复、查看已审核留言
- 管理员：审核留言、删除留言、回复
"""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.guestbook import GuestbookService
from app.schemas.guestbook import GuestbookCreate, GuestbookMessageOut, GuestbookReview
from app.utils.response import ApiResponse
from app.utils.dependencies import get_current_user, get_current_admin, get_optional_user
from app.models.user import User

router = APIRouter(prefix="/guestbook", tags=["留言板"])


@router.get("/messages")
async def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """获取已审核的留言列表（访客可访问）"""
    items, pagination = await GuestbookService.list_messages(
        db, page=page, page_size=page_size, approved_only=True
    )
    data = [GuestbookMessageOut.model_validate_custom(m).model_dump() for m in items]

    # 过滤回复中的敏感信息
    for msg in data:
        msg.pop("is_approved", None)
        for reply in msg.get("replies", []):
            reply.pop("is_approved", None)

    return ApiResponse.success({
        "items": data,
        "pagination": pagination.model_dump(),
    })


@router.get("/messages/admin")
async def list_all_messages_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """管理员查看所有留言（含未审核）"""
    items, pagination = await GuestbookService.list_messages(
        db, page=page, page_size=page_size, approved_only=False
    )
    return ApiResponse.success({
        "items": [GuestbookMessageOut.model_validate_custom(m).model_dump() for m in items],
        "pagination": pagination.model_dump(),
    })


@router.post("/messages")
async def create_message(
    data: GuestbookCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """
    创建留言/回复（访客可访问）
    - 自动经过敏感词过滤
    - 新留言默认待审核，管理员留言自动通过
    """
    # 如果 parent_id 存在，确保父留言存在
    if data.parent_id:
        from sqlalchemy import select
        from app.models.guestbook import GuestbookMessage
        result = await db.execute(
            select(GuestbookMessage).where(GuestbookMessage.id == data.parent_id)
        )
        parent = result.scalar_one_or_none()
        if parent is None:
            return ApiResponse.not_found("回复的目标留言不存在")

    is_admin = current_user is not None and current_user.role.value == "admin"
    ip = request.client.host if request else None
    msg = await GuestbookService.create_message(db, data, ip_address=ip, is_admin=is_admin)
    await db.commit()

    message = "留言已提交，审核通过后将对外显示"
    if is_admin:
        message = "留言成功"

    return ApiResponse.success(
        GuestbookMessageOut.model_validate_custom(msg).model_dump(),
        message,
    )


@router.post("/messages/admin")
async def create_admin_reply(
    data: GuestbookCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """管理员回复留言"""
    ip = request.client.host if request else None
    msg = await GuestbookService.create_message(db, data, ip_address=ip, is_admin=True)
    await db.commit()
    return ApiResponse.success(
        GuestbookMessageOut.model_validate_custom(msg).model_dump(),
        "回复成功",
    )


@router.put("/messages/{message_id}/review")
async def review_message(
    message_id: int,
    data: GuestbookReview,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """审核留言（管理员）"""
    msg = await GuestbookService.review_message(db, message_id, data.is_approved)
    if msg is None:
        return ApiResponse.not_found("留言不存在")
    await db.commit()
    return ApiResponse.success(message="审核完成")


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除留言（管理员）"""
    ok = await GuestbookService.delete_message(db, message_id)
    await db.commit()
    if not ok:
        return ApiResponse.not_found("留言不存在")
    return ApiResponse.success(message="留言已删除")
