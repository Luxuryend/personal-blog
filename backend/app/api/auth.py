"""
认证 API
包括登录、获取当前用户信息、用户注册（访客自助注册）。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo, UserCreate, UserUpdate
from app.services.auth import AuthService
from app.utils.response import ApiResponse
from app.utils.dependencies import get_current_user, get_current_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    - 校验用户名密码
    - 成功返回 JWT Token
    """
    user = await AuthService.authenticate(db, body.username, body.password)
    if not user:
        return ApiResponse.unauthorized("用户名或密码错误")

    token = AuthService.create_access_token(user.id, user.role.value)
    return ApiResponse.success({
        "access_token": token,
        "token_type": "bearer",
        "user": UserInfo.model_validate(user).model_dump(),
    })


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return ApiResponse.success(UserInfo.model_validate(current_user).model_dump())


@router.put("/me")
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新当前用户信息
    可修改昵称和密码（管理员密码仅通过 .env 配置修改）
    """
    if body.nickname is not None:
        current_user.nickname = body.nickname
    if body.password is not None and current_user.role != UserRole.ADMIN:
        current_user.password_hash = AuthService.hash_password(body.password)

    await db.flush()
    await db.commit()
    return ApiResponse.success(UserInfo.model_validate(current_user).model_dump(), "个人信息已更新")


@router.post("/register")
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    访客自助注册
    - 默认角色为 VISITOR
    - 管理员账户只能通过 .env 初始化
    """
    from sqlalchemy import select
    from app.models.user import User as UserModel

    # 检查用户名是否已存在
    result = await db.execute(select(UserModel).where(UserModel.username == body.username))
    if result.scalar_one_or_none():
        return ApiResponse.bad_request("用户名已存在")

    user = await AuthService.create_user(
        db, body.username, body.password, body.nickname, UserRole.VISITOR
    )
    await db.commit()
    return ApiResponse.success(UserInfo.model_validate(user).model_dump(), "注册成功")
