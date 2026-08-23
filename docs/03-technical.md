# 技术细节：zw-blog

| 项 | 内容 |
| --- | --- |
| 版本 | v1 |
| 对应 PRD | [01-prd.md](01-prd.md) |
| 对应架构 | [02-architecture.md](02-architecture.md) |

本文是实现合同。字段名、路径、状态值以本文为准；User Stories 与 GitHub Issues 必须引用这些名字。

## 1. 技术版本

| 层 | 选型 | 版本下限 |
| --- | --- | --- |
| 语言 | Python | 3.12 |
| API | FastAPI + Uvicorn | FastAPI 0.115+ |
| ORM / SQL | SQLAlchemy 2.x + Alembic | 2.0+ |
| 校验 | Pydantic v2 | 2.0+ |
| 前端 | React + Vite + TypeScript + React Router | React 18 / Vite 5 / TS 5 |
| 测试 | pytest、httpx、Vitest、Testing Library | — |
| 容器 | Docker Compose Compose Specification | — |

不引入 Celery、Nginx、Redis、PostgreSQL（v1）。

## 2. 仓库目录

```text
zw-blog/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── deps.py
│   │   ├── errors.py
│   │   └── routers/
│   │       ├── health.py
│   │       ├── auth.py
│   │       ├── articles.py
│   │       ├── tags.py
│   │       ├── comments.py
│   │       ├── about.py
│   │       ├── admin.py
│   │       └── uploads.py
│   └── tests/
└── web/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── api/client.ts
    │   ├── pages/
    │   └── components/
    └── src/__tests__/
```

数据与上传不进 Git：`data/blog.db`、`data/uploads/`。

## 3. 环境变量

文件：根目录 `.env`（不提交），模板 `.env.example`。

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `ADMIN_USERNAME` | 是 | 作者登录名 |
| `ADMIN_PASSWORD` | 是 | 作者密码，明文仅存在环境中；校验时用恒定时间比较 |
| `SESSION_SECRET` | 是 | 签名 Cookie，至少 32 字节随机串 |
| `GITHUB_CLIENT_ID` | 是（评论） | GitHub OAuth App |
| `GITHUB_CLIENT_SECRET` | 是（评论） | 仅服务端 |
| `GITHUB_OAUTH_CALLBACK_URL` | 是 | 必须与 GitHub App 中填写的一致，例如 `http://localhost:8000/api/auth/github/callback` |
| `PUBLIC_WEB_ORIGIN` | 是 | 前端 origin，用于 CORS 与 OAuth 回跳，例如 `http://localhost:5173` |
| `DATABASE_URL` | 否 | 默认 `sqlite+aiosqlite:///./data/blog.db` |
| `UPLOAD_DIR` | 否 | 默认 `./data/uploads` |
| `COOKIE_SECURE` | 否 | 生产 `true` |
| `VITE_API_BASE_URL` | 前端 | 开发留空（走 Vite 代理）；生产如 `http://localhost:8000` |

## 4. 数据模型

SQLite，WAL。时间一律 UTC ISO 8601 字符串或 `DateTime`，API 输出带 `Z` 的 UTC。

### 4.1 `articles`

| 列 | 类型 | 约束 |
| --- | --- | --- |
| `id` | INTEGER | PK |
| `slug` | TEXT | UNIQUE，未发布时可先占位；发布后对读者可见 |
| `title` | TEXT | NOT NULL |
| `body_md` | TEXT | NOT NULL，默认 `''` |
| `excerpt` | TEXT | 可空；空则列表用正文截断 160 字 |
| `cover_path` | TEXT | 可空，相对上传 URL |
| `status` | TEXT | `draft` \| `published`，默认 `draft` |
| `published_at` | DATETIME | 可空；首次发布写入，再发布不改（撤回后再发则更新） |
| `created_at` | DATETIME | NOT NULL |
| `updated_at` | DATETIME | NOT NULL |

`slug` 规则：`^[a-z0-9]+(?:-[a-z0-9]+)*$`，最长 80。创建时若未传，由标题生成拼音/英文 slug；冲突则拒绝并要求作者改（不自动加随机后缀，避免 URL 不可预期）。

### 4.2 `tags` / `article_tags`

`tags`：`id`、`name`（UNIQUE）、`slug`（UNIQUE）。  
`article_tags`：`article_id` + `tag_id` 联合主键，外键级联删除。

### 4.3 `comments`

| 列 | 类型 | 约束 |
| --- | --- | --- |
| `id` | INTEGER | PK |
| `article_id` | INTEGER | FK → articles，ON DELETE CASCADE |
| `github_id` | INTEGER | NOT NULL |
| `github_login` | TEXT | NOT NULL |
| `github_avatar_url` | TEXT | NOT NULL |
| `body` | TEXT | NOT NULL，1–2000 字符（按 Unicode 码点） |
| `created_at` | DATETIME | NOT NULL |

无软删除。作者删除即物理删除。

### 4.4 `about_page`

单行表（`id` 恒为 `1`）：`body_md` TEXT NOT NULL DEFAULT `''`，`updated_at`。

### 4.5 FTS5

虚拟表 `articles_fts`，字段 `title`、`body_md`，用 `article_id` 关联。  
仅 **published** 文章进入索引；撤回或删除时同步移除。查询使用 `MATCH`，结果再 join `articles` 保证 `status = 'published'`。

## 5. 统一错误体

HTTP 状态 +：

```json
{
  "error": {
    "code": "SLUG_CONFLICT",
    "message": "这个短链接已被占用"
  }
}
```

| code | HTTP | 何时 |
| --- | --- | --- |
| `UNAUTHORIZED` | 401 | 缺会话或凭据错误（登录失败也用此码，文案统一为「用户名或密码不正确」） |
| `FORBIDDEN` | 403 | 已登录但无权（v1 少用） |
| `NOT_FOUND` | 404 | 公开侧文章/标签不存在或未发布 |
| `VALIDATION_ERROR` | 422 | 字段不合法、空评论、文件类型/大小 |
| `SLUG_CONFLICT` | 409 | slug 重复 |
| `OAUTH_FAILED` | 400 | GitHub 换票或 state 校验失败 |

## 6. HTTP API

除特别说明外：JSON，`Content-Type: application/json`。Cookie 随请求（前端 `credentials: 'include'`）。

前缀一律 `/api`。

### 6.1 健康检查

`GET /api/health` → `200` `{"status":"ok"}`

### 6.2 作者认证

`POST /api/auth/admin/login`

```json
{ "username": "string", "password": "string" }
```

成功 `200`：`{"ok":true}`，并 Set-Cookie `admin_session`。失败 `401` `UNAUTHORIZED`。

`POST /api/auth/admin/logout` → 清 `admin_session`，`200` `{"ok":true}`。  
`GET /api/auth/admin/me` → `200` `{"role":"admin","username":"..."}` 或 `401`。

### 6.3 读者 GitHub OAuth

`GET /api/auth/github?next=/posts/{slug}`

- 生成随机 `state`，放入短时签名 cookie `oauth_state`（5 分钟）。
- 重定向 GitHub：`scope=read:user`，`redirect_uri=${GITHUB_OAUTH_CALLBACK_URL}`。

`GET /api/auth/github/callback?code=&state=`

- 校验 `state`；用 `code` 换 access_token；请求 `GET https://api.github.com/user`。
- 需要字段：`id`、`login`、`avatar_url`。
- Set-Cookie `reader_session`（载荷：`github_id, login, avatar_url`）。
- 302 到 `${PUBLIC_WEB_ORIGIN}{next}`，`next` 必须是站点内相对路径（以 `/` 开头且不含 `//`），否则回 `/`。

`POST /api/auth/github/logout` → 清 `reader_session`。  
`GET /api/auth/github/me` → `200` `{"github_id","login","avatar_url"}` 或 `401`。

测试中 GitHub HTTP 必须 mock，禁止打真实 api.github.com。

### 6.4 公开文章

`GET /api/articles?page=1&page_size=10&tag={slug}&q={keyword}`

- 只返回 `published`。
- `page` 从 1 起；`page_size` 默认 10，最大 50。
- `tag` 与 `q` 可同时存在（AND）。
- `q` 缺省或空白：普通列表，不走 FTS。
- 响应：

```json
{
  "items": [
    {
      "slug": "hello",
      "title": "...",
      "excerpt": "...",
      "cover_path": null,
      "published_at": "2026-08-23T00:00:00Z",
      "tags": [{ "name": "技术", "slug": "tech" }]
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1
}
```

`GET /api/articles/{slug}` → 已发布全文：

```json
{
  "slug": "hello",
  "title": "...",
  "body_md": "...",
  "excerpt": "...",
  "cover_path": null,
  "published_at": "...",
  "updated_at": "...",
  "tags": [{ "name": "技术", "slug": "tech" }]
}
```

草稿或未知 slug → `404 NOT_FOUND`，body 不出现草稿标题。

### 6.5 标签

`GET /api/tags` → 仅包含「至少一篇已发布文章」的标签：

```json
{ "items": [{ "name": "技术", "slug": "tech", "article_count": 3 }] }
```

### 6.6 评论（公开读 + 读者写）

`GET /api/articles/{slug}/comments`  
文章必须已发布，否则 `404`。按 `created_at` 正序。

```json
{
  "items": [
    {
      "id": 1,
      "github_login": "octocat",
      "github_avatar_url": "https://...",
      "body": "写得清楚",
      "created_at": "..."
    }
  ]
}
```

`POST /api/articles/{slug}/comments`  
Cookie：`reader_session`。Body：`{"body":"..."}`。  
成功 `201` 返回刚创建的评论对象。空/超长 → `422`。未登录 → `401`。

### 6.7 关于我

`GET /api/about` → `{"body_md":"..."}`，从未写过则为 `""`。

### 6.8 作者：文章与关于我

均需 `admin_session`。

`GET /api/admin/articles?status=draft|published&page=&page_size=`  
条目含 `id, slug, title, status, published_at, updated_at, tags`。

`POST /api/admin/articles`

```json
{
  "title": "必填",
  "body_md": "",
  "excerpt": null,
  "slug": null,
  "cover_path": null,
  "tag_names": ["技术"]
}
```

成功 `201`，`status` 恒为 `draft`。`tag_names` 中不存在的标签当场创建。

`GET /api/admin/articles/{id}`  
`PATCH /api/admin/articles/{id}` 可改标题、正文、摘要、slug、封面、`tag_names`。  
`DELETE /api/admin/articles/{id}` → `204`，评论级联删除。

`POST /api/admin/articles/{id}/publish` → `200`，要求 `title` 非空、`slug` 合法且唯一。  
`POST /api/admin/articles/{id}/unpublish` → 回到 `draft`，从 FTS 移除；`published_at` 置空。

`PUT /api/admin/about` body `{"body_md":"..."}`。

### 6.9 作者：删评与上传

`DELETE /api/admin/comments/{id}` → `204`。不存在 `404`。

`POST /api/admin/uploads`  
`multipart/form-data` 字段名 `file`。  
允许 `image/jpeg|png|gif|webp`，最大 5_242_880 字节。  
成功 `201` `{"url":"/api/uploads/{filename}"}`。  
`GET /api/uploads/{filename}` 公开可读（仅已保存文件）。

## 7. Cookie 与会话载荷

使用签名 Cookie（itsdangerous 或等效），不建 session 表。

| Cookie | 载荷 | 有效期 |
| --- | --- | --- |
| `admin_session` | `{ "role": "admin", "username": "..." }` | 7 天 |
| `reader_session` | `{ "github_id", "login", "avatar_url" }` | 30 天 |
| `oauth_state` | 随机 state | 5 分钟 |

`HttpOnly`、`Path=/`、`SameSite=Lax`。`COOKIE_SECURE=true` 时加 `Secure`。

## 8. Markdown 与 XSS

- 存储：原始 `body_md`，不在写入时预渲染 HTML。
- 展示：前端用 `react-markdown` + `remark-gfm` + `rehype-sanitize`。允许元素：`p, h1-h3, ul, ol, li, a, code, pre, blockquote, table, thead, tbody, tr, th, td, img, em, strong, hr`。`a[href]` 只允许 `http`/`https`/`mailto`；`img[src]` 只允许站点相对路径 `/api/uploads/` 或 `https`。
- 评论：`body` 当纯文本，React 默认转义即可，禁止当 HTML 插入。
- 代码高亮：`rehype-highlight` 或 `highlight.js`（FR-11）。

## 9. 前端约定

- React Router 路径与 PRD 第 4 节一致。
- `src/api/client.ts` 封装 `fetch`，`credentials: 'include'`。开发 `vite.config.ts`：

```ts
proxy: { "/api": "http://127.0.0.1:8000" }
```

- 后台编辑器：`<textarea>` 即可，v1 不做所见即所得。可提供「预览」切换，预览复用公开渲染组件。
- 文案中文。按钮：「保存草稿」「发布」「撤回为草稿」「删除评论」「使用 GitHub 登录」。

## 10. Docker

`docker-compose.yml` 仅两个服务：

```yaml
services:
  api:
    build: ./api
    ports: ["8000:8000"]
    env_file: .env
    volumes:
      - blog_data:/data
    environment:
      DATABASE_URL: sqlite+aiosqlite:////data/blog.db
      UPLOAD_DIR: /data/uploads
  web:
    build: ./web
    ports: ["4173:4173"]
    environment:
      VITE_API_BASE_URL: http://localhost:8000
volumes:
  blog_data:
```

- `api` Dockerfile：安装依赖，`uvicorn app.main:app --host 0.0.0.0 --port 8000`。启动时跑 Alembic upgrade。
- `web` Dockerfile：`npm ci && npm run build`，`npm run preview -- --host 0.0.0.0 --port 4173`。
- 不添加 nginx 服务、不添加 redis 服务。

## 11. 测试约定

| 范围 | 命令 | 位置 |
| --- | --- | --- |
| API | `pytest`（工作目录 `api/`） | `api/tests/test_*.py` |
| Web | `npm test`（工作目录 `web/`） | `web/src/__tests__/` |

API 测试使用临时 SQLite（pytest fixture），不碰开发库。OAuth 测试 mock token 与 `/user`。  
每个 Issue 正文里的「先写的测试」必须对应到上表路径中的具体函数名。

关闭 Issue 的 comment 至少包含：命令、通过的用例名、简短结果。

## 12. GitHub OAuth App 配置备忘

作者在 GitHub → Settings → Developer settings → OAuth Apps 创建应用：

- Homepage URL：`PUBLIC_WEB_ORIGIN`
- Authorization callback URL：`GITHUB_OAUTH_CALLBACK_URL`

本地与生产各一个 App，或同一 App 只填当前环境回调（v1 不要求多回调）。
