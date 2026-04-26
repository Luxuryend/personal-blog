"""
博客服务
封装博客文章的 CRUD、分类/标签管理等业务逻辑。
"""

from math import ceil
from sqlalchemy import select, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.blog import Blog, BlogCategory, BlogTag, BlogTagRelation
from app.schemas.blog import BlogCreate, BlogUpdate, CategoryCreate, TagCreate
from app.schemas.common import Pagination


class BlogService:
    """博客业务逻辑"""

    # ── 分类 ────────────────────────────────────────────────

    @staticmethod
    async def list_categories(db: AsyncSession) -> list[BlogCategory]:
        result = await db.execute(select(BlogCategory).order_by(BlogCategory.id))
        return list(result.scalars().all())

    @staticmethod
    async def create_category(db: AsyncSession, data: CategoryCreate) -> BlogCategory:
        cat = BlogCategory(**data.model_dump())
        db.add(cat)
        await db.flush()
        return cat

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        result = await db.execute(select(BlogCategory).where(BlogCategory.id == category_id))
        cat = result.scalar_one_or_none()
        if not cat:
            return False
        await db.delete(cat)
        await db.flush()
        return True

    # ── 标签 ────────────────────────────────────────────────

    @staticmethod
    async def list_tags(db: AsyncSession) -> list[BlogTag]:
        result = await db.execute(select(BlogTag).order_by(BlogTag.id))
        return list(result.scalars().all())

    @staticmethod
    async def create_tag(db: AsyncSession, data: TagCreate) -> BlogTag:
        tag = BlogTag(**data.model_dump())
        db.add(tag)
        await db.flush()
        return tag

    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
        result = await db.execute(select(BlogTag).where(BlogTag.id == tag_id))
        tag = result.scalar_one_or_none()
        if not tag:
            return False
        await db.delete(tag)
        await db.flush()
        return True

    # ── 文章 ────────────────────────────────────────────────

    @staticmethod
    async def list_blogs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        category_id: int | None = None,
        tag_id: int | None = None,
        published_only: bool = True,
    ) -> tuple[list[Blog], Pagination]:
        """
        分页查询文章列表。
        published_only=True 时只返回已发布的（对外展示）；
        published_only=False 时返回全部（管理后台用）。
        """
        query = select(Blog).options(
            selectinload(Blog.tags),
        )

        if published_only:
            query = query.where(Blog.is_published == True)
        if category_id:
            query = query.where(Blog.category_id == category_id)
        if tag_id:
            # 通过多对多关联过滤
            query = query.where(Blog.id.in_(
                select(BlogTagRelation.blog_id).where(BlogTagRelation.tag_id == tag_id)
            ))

        # 总条数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # 分页 + 排序
        query = query.order_by(Blog.is_top.desc(), Blog.created_at.desc())
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
    async def get_blog_by_slug(db: AsyncSession, slug: str) -> Blog | None:
        """通过 slug 获取文章详情"""
        result = await db.execute(
            select(Blog)
            .options(selectinload(Blog.tags))
            .where(Blog.slug == slug)
        )
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def get_blog_by_id(db: AsyncSession, blog_id: int) -> Blog | None:
        result = await db.execute(
            select(Blog)
            .options(selectinload(Blog.tags))
            .where(Blog.id == blog_id)
        )
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def create_blog(db: AsyncSession, data: BlogCreate, author_id: int) -> Blog:
        """创建文章"""
        blog = Blog(
            title=data.title,
            slug=data.slug,
            content=data.content,
            summary=data.summary,
            cover_image=data.cover_image,
            is_published=data.is_published,
            is_top=data.is_top,
            category_id=data.category_id,
            author_id=author_id,
        )
        db.add(blog)
        await db.flush()

        # 关联标签
        if data.tag_ids:
            for tag_id in data.tag_ids:
                db.add(BlogTagRelation(blog_id=blog.id, tag_id=tag_id))
            await db.flush()

        # 重新查询以加载 tags 关联
        result = await db.execute(
            select(Blog)
            .options(selectinload(Blog.tags))
            .where(Blog.id == blog.id)
        )
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def update_blog(db: AsyncSession, blog: Blog, data: BlogUpdate) -> Blog:
        """更新文章"""
        update_data = data.model_dump(exclude_unset=True)
        tag_ids = update_data.pop("tag_ids", None)

        for field, value in update_data.items():
            setattr(blog, field, value)

        # 更新标签关联
        if tag_ids is not None:
            await db.execute(
                delete(BlogTagRelation).where(BlogTagRelation.blog_id == blog.id)
            )
            for tag_id in tag_ids:
                db.add(BlogTagRelation(blog_id=blog.id, tag_id=tag_id))

        await db.flush()

        # 重新查询以加载 tags 关联
        result = await db.execute(
            select(Blog)
            .options(selectinload(Blog.tags))
            .where(Blog.id == blog.id)
        )
        return result.unique().scalar_one_or_none()

    @staticmethod
    async def delete_blog(db: AsyncSession, blog: Blog):
        """删除文章"""
        await db.delete(blog)
        await db.flush()

    @staticmethod
    async def increment_view_count(db: AsyncSession, blog: Blog):
        """增加浏览次数"""
        blog.view_count += 1
        await db.flush()
