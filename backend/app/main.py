"""
FastAPI 应用入口
注册路由、中间件、静态文件服务、启动事件（初始化数据库）。
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import auth, blog, share, guestbook
from app.utils.response import ApiResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    await init_db()
    yield


app = FastAPI(
    title="Personal Website API",
    description="个人网站后端 API，包含博客、文件分享、留言板模块",
    version="1.0.0",
    lifespan=lifespan,
)

# ── 注册路由 ───────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")
app.include_router(blog.router, prefix="/api")
app.include_router(share.router, prefix="/api")
app.include_router(guestbook.router, prefix="/api")


# ── 静态文件服务（上传的文件） ──────────────────────────────
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


# ── 健康检查 ───────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return ApiResponse.success({"status": "ok"}, "服务运行正常")


# ── 全局异常处理 ───────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """兜底异常处理，避免服务器返回 500 裸信息"""
    import traceback
    traceback.print_exc()
    return ApiResponse.error(500, f"服务器内部错误: {str(exc)}")
