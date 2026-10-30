# zw-blog

个人博客系统：Vite + React 前端，FastAPI 后端，SQLite 数据库。

## 功能特性

✅ **文章管理**: 创建、编辑、发布、撤回文章，支持草稿<br/>
✅ **Markdown 渲染**: 支持 GFM (GitHub Flavored Markdown)，代码语法高亮<br/>
✅ **标签系统**: 为文章添加标签，按标签筛选浏览<br/>
✅ **全文搜索**: 基于 SQLite FTS5 的高效搜索<br/>
✅ **评论功能**: GitHub OAuth 登录后发表评论<br/>
✅ **响应式设计**: 桌面和移动端均可良好使用<br/>
✅ **后台管理**: 作者登录后可管理文章、评论和关于页<br/>

## 快速开始

### 使用 Docker Compose（推荐）

这是最简单的运行方式，适合生产部署和快速体验。

```bash
# 1. 克隆仓库
git clone https://github.com/showboat-dev/zw-blog.git
cd zw-blog

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，至少设置：
# - ADMIN_USERNAME 和 ADMIN_PASSWORD（后台登录凭据）
# - SESSION_SECRET（至少 32 个随机字符）

# 3. 启动服务
docker compose up --build

# 4. 访问应用
# 前端: http://localhost:4173
# API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

**首次启动**时，API 容器会自动运行种子脚本，创建 3 篇示例文章和标签，方便体验。

**后台管理**：访问 http://localhost:4173/admin/login，使用 `.env` 中配置的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 登录。

**数据持久化**：文章数据和上传的图片保存在 Docker volume `blog_data` 中。

### 本地开发

需要 Python 3.12+ 和 Node.js 20+。

#### 1. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件配置必需的环境变量
```

#### 2. 启动 API 后端

```bash
cd api

# 安装依赖
python -m pip install -e ".[dev]"

# 创建数据库并填充示例数据（可选）
python seed.py

# 启动开发服务器
python -m uvicorn app.main:app --reload --port 8000
```

API 健康检查: `curl http://localhost:8000/api/health`

#### 3. 启动前端

打开新终端：

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动。开发模式下，`/api` 请求会自动代理到后端。

## 项目结构

```
.
├── api/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 应用入口
│   │   ├── models.py     # 数据模型
│   │   ├── routers/      # API 路由
│   │   └── services/     # 业务逻辑
│   ├── tests/            # 后端测试
│   ├── seed.py           # 数据库种子脚本
│   └── pyproject.toml    # Python 依赖
├── web/              # React 前端
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   └── api/          # API 客户端
│   ├── tests/            # 前端测试
│   └── package.json      # Node 依赖
├── docs/             # 项目文档
├── design-system/    # 设计系统
├── prototype/        # 原型 HTML
├── docker-compose.yml    # Docker Compose 配置
└── README.md
```

## 运行测试

### 后端测试

```bash
cd api
python -m pytest -v
```

全部 25 个测试应该通过。

### 前端测试

```bash
cd web
npm test
```

全部 14 个测试应该通过。

## 环境变量说明

在 `.env` 文件中配置以下变量（参考 `.env.example`）：

### 必需变量

- `ADMIN_USERNAME`: 后台管理员用户名
- `ADMIN_PASSWORD`: 后台管理员密码
- `SESSION_SECRET`: 会话加密密钥（至少 32 个随机字符）

### GitHub OAuth（可选，评论功能需要）

- `GITHUB_CLIENT_ID`: GitHub OAuth App 的 Client ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth App 的 Client Secret
- `GITHUB_OAUTH_CALLBACK_URL`: OAuth 回调地址（默认 `http://localhost:8000/api/auth/github/callback`）

如何创建 GitHub OAuth App：
1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. 填写应用信息，Authorization callback URL 设为上述回调地址
4. 创建后获取 Client ID 和 Secret

### 其他配置

- `DATABASE_URL`: 数据库连接字符串（默认 SQLite）
- `UPLOAD_DIR`: 上传文件保存目录
- `PUBLIC_WEB_ORIGIN`: 前端地址（用于 CORS 配置）
- `COOKIE_SECURE`: 生产环境设为 `true`

## 使用指南

### 读者端功能

- **浏览文章**: 首页显示已发布的文章列表，按发布时间倒序
- **阅读文章**: 点击文章标题查看完整内容，支持 Markdown 和代码高亮
- **按标签筛选**: 点击标签查看该标签下的所有文章
- **搜索文章**: 使用搜索框查找标题或正文中的关键词
- **查看关于**: 了解博客作者信息
- **发表评论**: 使用 GitHub 账号登录后可以评论（需配置 GitHub OAuth）

### 作者端功能

1. **登录后台**: 访问 `/admin/login`，使用配置的管理员凭据登录
2. **管理文章**:
   - 创建新文章（默认为草稿状态）
   - 编辑文章内容、标签、封面等
   - 发布草稿或撤回已发布的文章
   - 删除文章
3. **上传图片**: 编辑文章时可上传配图，支持 jpg/png/gif/webp
4. **管理标签**: 写文章时可创建或选择已有标签
5. **编辑关于页**: 自定义博客的关于页内容
6. **删除评论**: 管理不当评论

## API 文档

启动 API 后访问 http://localhost:8000/docs 查看自动生成的交互式 API 文档（Swagger UI）。

主要端点：

- `GET /api/health` - 健康检查
- `GET /api/articles` - 获取已发布文章列表（支持分页、搜索）
- `GET /api/articles/{slug}` - 获取文章详情
- `GET /api/tags` - 获取标签列表
- `GET /api/about` - 获取关于页内容
- `POST /api/auth/admin/login` - 管理员登录
- `POST /api/admin/articles` - 创建文章（需要管理员权限）
- `POST /api/admin/articles/{id}/publish` - 发布文章

## 技术架构

详细的技术文档请参考 `docs/` 目录：

- `01-prd.md` - 产品需求文档
- `02-architecture.md` - 架构设计
- `03-technical.md` - 技术细节
- `04-user-stories.md` - 用户故事

### 技术栈

**后端 (api/)**
- FastAPI - 现代异步 Web 框架
- SQLAlchemy - ORM
- SQLite - 数据库，使用 FTS5 实现全文搜索
- aiosqlite - 异步 SQLite 驱动
- Pydantic - 数据验证

**前端 (web/)**
- React 18 - UI 框架
- Vite - 构建工具
- React Router - 路由
- react-markdown - Markdown 渲染
- rehype-sanitize - 防止 XSS
- rehype-highlight - 代码语法高亮

**部署**
- Docker & Docker Compose
- 无需 Nginx、Redis 等额外依赖

## 常见问题

### Docker Compose 启动失败？

- 确保 Docker 和 Docker Compose 已安装
- 检查 8000 和 4173 端口是否被占用
- 查看容器日志：`docker compose logs api` 或 `docker compose logs web`

### 本地开发时前端无法连接 API？

- 确保 API 在 8000 端口运行
- 检查 `.env` 文件中的配置
- 开发模式下，Vite 自动代理 `/api` 到 `http://localhost:8000`

### GitHub OAuth 登录失败？

- 确认 `.env` 中的 `GITHUB_CLIENT_ID` 和 `GITHUB_CLIENT_SECRET` 正确
- 检查 GitHub OAuth App 的回调 URL 配置
- 本地开发时使用 `http://localhost:8000/api/auth/github/callback`

### 如何备份数据？

**Docker 部署**：
```bash
# 备份 volume
docker run --rm -v blog_data:/data -v $(pwd):/backup alpine tar czf /backup/blog-backup.tar.gz /data
```

**本地开发**：
```bash
# 直接复制数据目录
cp -r api/data/ backup/
```

### 如何重置数据库？

**Docker 部署**：
```bash
docker compose down -v  # 删除 volume
docker compose up --build  # 重新启动，会自动创建示例数据
```

**本地开发**：
```bash
rm -rf api/data/  # 删除数据目录
python api/seed.py  # 重新创建示例数据
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**仓库**: https://github.com/showboat-dev/zw-blog
