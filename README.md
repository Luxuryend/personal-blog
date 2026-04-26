# 个人网站 (Personal Website)

基于 **FastAPI + Vue 3** 的个人网站，包含博客、文件分享、留言板三大模块。

## 技术栈

| 层    | 技术                                                         |
| ----- | ------------------------------------------------------------ |
| 后端  | Python FastAPI, SQLAlchemy (异步), SQLite/PostgreSQL, JWT, Pydantic v2 |
| 前端  | Vue 3 (Composition API), Vite, Pinia, Vue Router, Tailwind CSS, Axios |
| 部署  | Docker + Nginx                                               |

## 项目结构

```
personal-website/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层（auth, blog, share, guestbook）
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 请求/响应定义
│   │   ├── services/           # 业务逻辑层
│   │   └── utils/              # 工具（统一响应、敏感词过滤、鉴权依赖）
│   ├── main.py                 # 应用入口
│   ├── config.py               # 配置（.env）
│   ├── database.py             # 数据库引擎 & 会话
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/                # Axios 封装 & 各模块 API
│       ├── router/             # Vue Router 路由
│       ├── stores/             # Pinia 状态管理
│       ├── layouts/            # 布局组件
│       └── views/              # 页面组件
├── docker-compose.yml
└── README.md
```

## 快速启动

### 方式一：本地开发

**后端：**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173 即可访问。

### 方式二：Docker 部署

```bash
docker-compose up -d --build
```

访问 http://localhost。

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

### 统一响应格式

所有 API 返回格式：

```json
{
  "code": 0,        // 0 成功，非 0 错误
  "data": {},       // 数据
  "message": "ok"   // 描述
}
```

### 模块 API

#### 认证 `/api/auth`

| 方法   | 路径             | 说明             | 权限     |
| ------ | ---------------- | ---------------- | -------- |
| POST   | /api/auth/login  | 登录，获取 Token | 公开     |
| GET    | /api/auth/me     | 获取当前用户     | 登录用户 |
| POST   | /api/auth/register | 注册新用户     | 公开     |

#### 博客 `/api/blog`

| 方法   | 路径                          | 说明         | 权限     |
| ------ | ----------------------------- | ------------ | -------- |
| GET    | /api/blog/posts               | 文章列表     | 公开     |
| GET    | /api/blog/posts/{slug_or_id}  | 文章详情     | 公开     |
| POST   | /api/blog/posts               | 创建文章     | 管理员   |
| PUT    | /api/blog/posts/{id}          | 更新文章     | 管理员   |
| DELETE | /api/blog/posts/{id}          | 删除文章     | 管理员   |
| GET    | /api/blog/categories          | 分类列表     | 公开     |
| POST   | /api/blog/categories          | 创建分类     | 管理员   |
| DELETE | /api/blog/categories/{id}     | 删除分类     | 管理员   |
| GET    | /api/blog/tags                | 标签列表     | 公开     |
| POST   | /api/blog/tags                | 创建标签     | 管理员   |
| DELETE | /api/blog/tags/{id}           | 删除标签     | 管理员   |

#### 文件分享 `/api/share`

| 方法   | 路径                              | 说明             | 权限     |
| ------ | --------------------------------- | ---------------- | -------- |
| POST   | /api/share/upload                 | 上传文件         | 管理员   |
| GET    | /api/share/files                  | 分享列表         | 公开     |
| GET    | /api/share/files/{id}             | 分享详情         | 公开     |
| POST   | /api/share/files/{id}/verify      | 验证提取码       | 公开     |
| GET    | /api/share/files/{id}/download    | 下载文件         | 公开     |
| DELETE | /api/share/files/{id}             | 删除分享         | 管理员   |
| GET    | /api/share/files/{id}/logs        | 访问日志         | 管理员   |

#### 留言板 `/api/guestbook`

| 方法   | 路径                               | 说明             | 权限     |
| ------ | ---------------------------------- | ---------------- | -------- |
| GET    | /api/guestbook/messages            | 已审核留言列表   | 公开     |
| POST   | /api/guestbook/messages            | 创建留言         | 公开     |
| POST   | /api/guestbook/messages/admin      | 管理员回复       | 管理员   |
| PUT    | /api/guestbook/messages/{id}/review | 审核留言         | 管理员   |
| DELETE | /api/guestbook/messages/{id}       | 删除留言         | 管理员   |

## 功能特性

### 博客
- Markdown 存储与渲染
- 分类 & 标签聚合
- 置顶 & 发布控制
- 浏览次数统计

### 文件分享
- 图片/文件上传，MIME 类型校验
- 提取码保护
- 链接有效期 & 下载次数限制
- 本地存储 / OSS 可切换
- 访问日志

### 留言板
- 二级评论（回复功能）
- 敏感词过滤（DFA 算法）
- 留言审核机制

### 鉴权
- JWT Token 鉴权
- 管理员 / 访客角色区分
- Axios 请求拦截器自动附加 Token

## 默认管理员

- 用户名：`admin`
- 密码：`admin123456`

首次启动数据库时自动创建，请在生产环境中修改密码并更新 `.env`。
