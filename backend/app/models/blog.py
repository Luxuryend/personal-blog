"""
博客模块模型
- Blog：文章主体，content 以 Markdown 格式存储
- BlogCategory：分类（一对多）
- BlogTag / BlogTagRelation：标签（多对多）
"""

from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BlogCategory(Base):
    """博客分类"""
    __tablename__ = "blog_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="URL 友好的标识")
    description: Mapped[str | None] = mapped_column(String(200), comment="分类描述")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class BlogTag(Base):
    """博客标签"""
    __tablename__ = "blog_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, comment="标签名称")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class BlogTagRelation(Base):
    """文章-标签 多对多关联表"""
    __tablename__ = "blog_tag_relations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    blog_id: Mapped[int] = mapped_column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_tags.id", ondelete="CASCADE"))


class Blog(Base):
    """博客文章"""
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="文章标题")
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, comment="URL 标识")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="Markdown 正文")
    summary: Mapped[str | None] = mapped_column(String(500), comment="摘要")
    cover_image: Mapped[str | None] = mapped_column(String(500), comment="封面图 URL")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否发布")
    is_top: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否置顶")
    view_count: Mapped[int] = mapped_column(Integer, default=0, comment="浏览次数")
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("blog_categories.id"), comment="所属分类")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, comment="作者 ID")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # ORM 关系 —— 使用 raise 策略，所有查询必须显式 selectinload
    category = relationship("BlogCategory", lazy="joined")
    tags = relationship("BlogTag", secondary="blog_tag_relations", lazy="raise", viewonly=True)
