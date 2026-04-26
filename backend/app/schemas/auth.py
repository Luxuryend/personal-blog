"""
认证相关请求/响应 Schema
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class TokenResponse(BaseModel):
    """登录成功返回的 Token"""
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    """用户公开信息"""
    id: int
    username: str
    nickname: str | None
    role: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """创建用户（注册）"""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str | None = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: str | None = Field(None, max_length=50)
    password: str | None = Field(None, min_length=6, max_length=128)
