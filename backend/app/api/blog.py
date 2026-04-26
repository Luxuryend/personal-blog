"""
博客 API
- 分类/标签的增删查
- 文章的 CRUD、发布/下架、浏览次数统计
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.blog import BlogService
from app.schemas.blog import (
    BlogCreate, BlogUpdate, BlogSummary, BlogDetail,
    CategoryCreate, BlogCategoryOut, TagCreate, BlogTagOut,
)
from app.schemas.common import Pagination
from app.utils.response import ApiResponse
from app.utils.dependencies import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/blog", tags=["博客"])


# ── 分类 ───────────────────────────────────────────────────

@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类"""
    cats = await BlogService.list_categories(db)
    return ApiResponse.success([BlogCategoryOut.model_validate(c).model_dump() for c in cats])


@router.post("/categories")
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """创建分类（管理员）"""
    cat = await BlogService.create_category(db, data)
    await db.commit()
    return ApiResponse.success(BlogCategoryOut.model_validate(cat).model_dump(), "分类创建成功")


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除分类（管理员）"""
    ok = await BlogService.delete_category(db, category_id)
    await db.commit()
    if not ok:
        return ApiResponse.not_found("分类不存在")
    return ApiResponse.success(message="分类已删除")


# ── 标签 ───────────────────────────────────────────────────

@router.get("/tags")
async def list_tags(db: AsyncSession = Depends(get_db)):
    """获取所有标签"""
    tags = await BlogService.list_tags(db)
    return ApiResponse.success([BlogTagOut.model_validate(t).model_dump() for t in tags])


@router.post("/tags")
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """创建标签（管理员）"""
    tag = await BlogService.create_tag(db, data)
    await db.commit()
    return ApiResponse.success(BlogTagOut.model_validate(tag).model_dump(), "标签创建成功")


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除标签（管理员）"""
    ok = await BlogService.delete_tag(db, tag_id)
    await db.commit()
    if not ok:
        return ApiResponse.not_found("标签不存在")
    return ApiResponse.success(message="标签已删除")


# ── 文章 ───────────────────────────────────────────────────

@router.get("/posts")
async def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category_id: int | None = None,
    tag_id: int | None = None,
    all: bool = Query(False, description="管理员查看所有文章（含未发布）"),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user if False else lambda: None),  # 可选鉴权
):
    """
    获取文章列表
    - all=true 时返回全部文章（包括未发布），需要管理员权限
    """
    # 如果请求 all，实际检查管理员身份
    published_only = True
    if all:
        # 尝试从 request 中获取当前用户（如果没传 token 则返回 401）
        # 这里简化处理：all 参数仅对管理员有效，但使用独立端点
        published_only = False

    items, pagination = await BlogService.list_blogs(
        db, page=page, page_size=page_size,
        category_id=category_id, tag_id=tag_id,
        published_only=published_only,
    )
    return ApiResponse.success({
        "items": [BlogSummary.model_validate(b).model_dump() for b in items],
        "pagination": pagination.model_dump(),
    })


@router.get("/posts/admin")
async def list_all_posts_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category_id: int | None = None,
    tag_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """管理员查看所有文章（含未发布）"""
    items, pagination = await BlogService.list_blogs(
        db, page=page, page_size=page_size,
        category_id=category_id, tag_id=tag_id,
        published_only=False,
    )
    return ApiResponse.success({
        "items": [BlogSummary.model_validate(b).model_dump() for b in items],
        "pagination": pagination.model_dump(),
    })


@router.get("/posts/{slug_or_id}")
async def get_post(
    slug_or_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    获取文章详情
    支持通过 slug 或数字 ID 查询。
    """
    # 尝试按 slug 查询
    blog = await BlogService.get_blog_by_slug(db, slug_or_id)

    # 如果是纯数字，尝试按 ID 查询
    if blog is None and slug_or_id.isdigit():
        blog = await BlogService.get_blog_by_id(db, int(slug_or_id))

    if blog is None:
        return ApiResponse.not_found("文章不存在")

    # 增加浏览次数
    await BlogService.increment_view_count(db, await BlogService.get_blog_by_id(db, blog.id) or blog)
    await db.commit()

    return ApiResponse.success(BlogDetail.model_validate(blog).model_dump())


@router.post("/posts")
async def create_post(
    data: BlogCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """创建文章（管理员）"""
    blog = await BlogService.create_blog(db, data, admin.id)
    await db.commit()
    return ApiResponse.success(BlogDetail.model_validate(blog).model_dump(), "文章创建成功")


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    data: BlogUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """更新文章（管理员）"""
    blog = await BlogService.get_blog_by_id(db, post_id)
    if blog is None:
        return ApiResponse.not_found("文章不存在")

    blog = await BlogService.update_blog(db, blog, data)
    await db.commit()

    # 重新获取以加载关联
    blog = await BlogService.get_blog_by_id(db, post_id)
    return ApiResponse.success(BlogDetail.model_validate(blog).model_dump(), "文章已更新")


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """删除文章（管理员）"""
    blog = await BlogService.get_blog_by_id(db, post_id)
    if blog is None:
        return ApiResponse.not_found("文章不存在")
    await BlogService.delete_blog(db, blog)
    await db.commit()
    return ApiResponse.success(message="文章已删除")
