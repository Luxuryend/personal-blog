"""
留言板服务
包含留言创建、审核、回复，以及敏感词过滤。
"""

from math import ceil
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.guestbook import GuestbookMessage
from app.schemas.guestbook import GuestbookCreate
from app.schemas.common import Pagination
from app.utils.sensitive import default_filter


class GuestbookService:
    """留言板业务逻辑"""

    @staticmethod
    async def create_message(
        db: AsyncSession,
        data: GuestbookCreate,
        ip_address: str | None = None,
        is_admin: bool = False,
    ) -> GuestbookMessage:
        """
        创建留言/回复。
        - 自动过滤敏感词
        - 管理员留言自动通过审核
        """
        # 敏感词过滤
        filtered_content = default_filter.filter(data.content)

        # 管理员发布留言强制使用 "admin" 昵称
        if is_admin:
            nickname = "admin"
        else:
            nickname = data.nickname or "匿名"
            if nickname.strip().lower() == "admin":
                nickname = "匿名"

        message = GuestbookMessage(
            content=filtered_content,
            nickname=nickname,
            email=data.email,
            website=data.website,
            parent_id=data.parent_id,
            is_admin_reply=is_admin,
            is_approved=is_admin,  # 管理员留言自动审核通过
            ip_address=ip_address,
        )
        db.add(message)
        await db.flush()

        # 如果是一级留言的回复，同时将父留言标记为通过（如有必要）
        if data.parent_id and is_admin:
            result = await db.execute(
                select(GuestbookMessage).where(GuestbookMessage.id == data.parent_id)
            )
            parent = result.scalar_one_or_none()
            if parent and not parent.is_approved:
                parent.is_approved = True
                await db.flush()

        return message

    @staticmethod
    async def list_messages(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        approved_only: bool = True,
    ) -> tuple[list[GuestbookMessage], Pagination]:
        """
        分页查询留言（仅一级留言，回复通过关系加载）。
        approved_only=True 时只返回已审核的留言。
        """
        query = (
            select(GuestbookMessage)
            .options(selectinload(GuestbookMessage.replies))
            .where(GuestbookMessage.parent_id.is_(None))  # 仅一级留言
        )

        if approved_only:
            query = query.where(GuestbookMessage.is_approved == True)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        query = query.order_by(desc(GuestbookMessage.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = list(result.unique().scalars().all())

        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if page_size > 0 else 0,
        )
        return items, pagination

    @staticmethod
    async def review_message(db: AsyncSession, message_id: int, is_approved: bool) -> GuestbookMessage | None:
        """审核留言"""
        result = await db.execute(
            select(GuestbookMessage).where(GuestbookMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg is None:
            return None
        msg.is_approved = is_approved
        await db.flush()
        return msg

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: int) -> bool:
        """删除留言"""
        result = await db.execute(
            select(GuestbookMessage).where(GuestbookMessage.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg is None:
            return False
        await db.delete(msg)
        await db.flush()
        return True
