# User Stories：zw-blog v1

对应 [PRD](01-prd.md)、[架构](02-architecture.md)、[技术细节](03-technical.md)。

拆 GitHub Issue 时：一条 Story 可拆成多张任务 Issue；Issue 标题带本页的 `US-xx`。验收用语与技术文档中的路径、状态值、错误码保持一致。

## 史诗一览

| 史诗 | Stories | PRD |
| --- | --- | --- |
| E1 工程骨架 | US-01 | FR-33, FR-34, FR-35 |
| E2 作者写与发 | US-02 … US-07 | FR-01–FR-07, FR-29, FR-31, FR-32 |
| E3 读者阅读 | US-08 … US-11 | FR-08–FR-11, FR-18, FR-19 |
| E4 标签与搜索 | US-12 … US-15 | FR-12–FR-17 |
| E5 评论 | US-16 … US-20 | FR-20–FR-26 |
| E6 作者会话 | US-21 … US-23 | FR-27, FR-28, FR-30 |
| E7 部署验收 | US-24 | FR-34, FR-35 |

---

## E1 工程骨架

### US-01 仓库能在本机和 Compose 里启动空服务

**作为** 作者，**我想** 用文档里的目录和 Compose 拉起 `web` 与 `api`，**以便** 后续功能有统一入口。

**PRD：** FR-33, FR-34, FR-35  
**验收：**

- Given 按 `.env.example` 配好环境，When 在 `api/` 启动 uvicorn，Then `GET /api/health` 返回 `{"status":"ok"}`
- Given 根目录 Compose 文件，When 检查服务列表，Then 只有 `web`、`api` 两个服务，没有 nginx / redis
- Given `data/` 与 `.env`，When 查看 `.gitignore`，Then 这些路径被忽略

**先写测试：** `api/tests/test_health.py::test_health_ok`

---

## E2 作者写与发

### US-02 作者能创建草稿

**作为** 作者，**我想** 先把未完成的文章存成草稿，**以便** 不怕写到一半丢失。

**PRD：** FR-01, FR-02, FR-29  
**验收：**

- Given 有效 `admin_session`，When `POST /api/admin/articles` 只传 `title`，Then `201` 且 `status` 为 `draft`，`published_at` 为 `null`
- Given 无作者会话，When 同一请求，Then `401 UNAUTHORIZED`
- Given 已建草稿，When `GET /api/articles`，Then `items` 不含该文
- Given 读者用草稿 slug 调 `GET /api/articles/{slug}`，Then `404 NOT_FOUND` 且 body 无草稿标题

**先写测试：**

- `api/tests/test_articles_admin.py::test_create_draft_requires_admin`
- `api/tests/test_articles_admin.py::test_create_draft_not_listed_publicly`
- `api/tests/test_articles_public.py::test_draft_slug_is_not_found`

### US-03 作者能把草稿改为已发布

**作为** 作者，**我想** 在写完后点发布，**以便** 读者立刻在首页看到。

**PRD：** FR-03, FR-08  
**验收：**

- Given 一篇有合法 `slug` 与非空 `title` 的草稿，When `POST /api/admin/articles/{id}/publish`，Then `status=published` 且写入 `published_at`
- Given 刚发布的文章，When `GET /api/articles`，Then 第一条为该文（按 `published_at` 倒序）
- Given `title` 为空，When 发布，Then `422 VALIDATION_ERROR`，状态仍为 `draft`

**先写测试：** `api/tests/test_articles_admin.py::test_publish_draft_appears_in_public_list`

### US-04 作者能撤回已发布文章

**作为** 作者，**我想** 把发错的文章撤回成草稿，**以便** 公开站不再展示。

**PRD：** FR-04  
**验收：**

- Given 已发布文章，When `POST /api/admin/articles/{id}/unpublish`，Then `status=draft`，`published_at` 为 `null`
- Given 撤回后，When 公开列表与详情，Then 都不再出现该文
- Given 撤回后的文章，When 再发布，Then 重新写入 `published_at`

**先写测试：** `api/tests/test_articles_admin.py::test_unpublish_hides_from_public`

### US-05 作者能编辑文章并处理 slug 冲突

**作为** 作者，**我想** 改标题、正文、摘要、封面、标签和 slug，**以便** 修正笔误和链接。

**PRD：** FR-05  
**验收：**

- Given 已有文章，When `PATCH` 修改 `title` 与 `body_md`，Then `updated_at` 变化且再读一致
- Given slug `a` 已被占用，When 把另一篇改成 `a`，Then `409 SLUG_CONFLICT`
- Given 非法 slug（空格或大写），When 保存，Then `422`

**先写测试：** `api/tests/test_articles_admin.py::test_slug_conflict_returns_409`

### US-06 作者能删除文章及其评论

**作为** 作者，**我想** 删掉不再需要的文章，**以便** 站点保持整洁。

**PRD：** FR-06  
**验收：**

- Given 文章下有评论，When `DELETE /api/admin/articles/{id}`，Then `204`，公开详情 `404`，原评论 `GET` 亦 `404`
- Given 无作者会话，When 删除，Then `401`

**先写测试：** `api/tests/test_articles_admin.py::test_delete_article_cascades_comments`

### US-07 后台列表能按状态筛选

**作为** 作者，**我想** 在后台只看草稿或只看已发布，**以便** 找到要改的那篇。

**PRD：** FR-07  
**验收：**

- Given 同时存在草稿与已发布，When `GET /api/admin/articles?status=draft`，Then 只含草稿
- When `status=published`，Then 只含已发布
- When 不传 `status`，Then 两种都在，分页字段符合技术文档

**先写测试：** `api/tests/test_articles_admin.py::test_admin_list_filter_by_status`

---

## E3 读者阅读

### US-08 读者能分页浏览已发布文章

**作为** 读者，**我想** 在首页按时间倒序翻页，**以便** 先看到新文。

**PRD：** FR-08  
**验收：**

- Given 11 篇已发布，When `page=1&page_size=10`，Then `items.length=10` 且 `total=11`
- Given 两篇 `published_at` 不同，Then 新的在前
- Given 列表项，Then 含 `title, excerpt, published_at, tags`，不含 `body_md`

**先写测试：** `api/tests/test_articles_public.py::test_public_list_pagination_and_order`

**前端：** 首页渲染列表；空列表展示「还没有文章」而不是空白。  
**先写测试（前端）：** `web/src/__tests__/HomePage.test.tsx`

### US-09 读者能阅读 Markdown 正文

**作为** 读者，**我想** 打开一篇文章看到排版后的正文，**以便** 读技术内容和感悟。

**PRD：** FR-09, FR-11  
**验收：**

- Given 正文含 GFM 表格与 ` ```python ` 代码块，When 打开详情，Then 表格与代码块被渲染，代码有高亮 class
- Given Markdown 含 `<script>`，When 渲染，Then 页面不执行脚本（消毒）
- Given 未知 slug，When 打开详情，Then 中文「文章不存在」

**先写测试：**

- `api/tests/test_articles_public.py::test_public_detail_returns_body_md`
- `web/src/__tests__/PostPage.test.tsx`（消毒与 404 文案）

### US-10 读者能查看关于我

**作为** 读者，**我想** 在关于页了解作者，**以便** 判断要不要继续读。

**PRD：** FR-18, FR-19  
**验收：**

- Given `about_page.body_md` 为空，When `GET /api/about`，Then `{"body_md":""}`，页面展示空状态「作者还没有写介绍」
- Given 作者 `PUT /api/admin/about`，When 再打开 `/about`，Then 渲染新 Markdown

**先写测试：** `api/tests/test_about.py::test_about_empty_and_update`

### US-11 作者能上传配图并写进文章

**作为** 作者，**我想** 上传一张图并得到 URL，**以便** 插进 Markdown。

**PRD：** FR-31, FR-32  
**验收：**

- Given jpeg < 5MB，When `POST /api/admin/uploads`，Then `201` 且 `url` 以 `/api/uploads/` 开头，`GET` 该 url 为 200
- Given `.exe` 或 6MB 文件，When 上传，Then `422 VALIDATION_ERROR`
- Given 无作者会话，When 上传，Then `401`

**先写测试：** `api/tests/test_uploads.py::test_upload_rejects_bad_type_and_anonymous`

---

## E4 标签与搜索

### US-12 写文章时能打标签

**作为** 作者，**我想** 给文章一个或多个标签，**以便** 把技术文和随笔分开。

**PRD：** FR-12  
**验收：**

- Given `tag_names: ["技术","随笔"]`，When 创建或 PATCH，Then 文章带这两个标签；库中新增不存在的 tag
- Given 同一 name 第二次使用，When 保存，Then 不产生重复 `tags` 行
- Given 公开详情，Then `tags` 含 `name` 与 `slug`

**先写测试：** `api/tests/test_tags.py::test_tag_names_create_or_reuse`

### US-13 读者能浏览标签及其文章

**作为** 读者，**我想** 先看有哪些标签再点进去，**以便** 只读某一类。

**PRD：** FR-13, FR-14  
**验收：**

- Given 标签只挂在草稿上，When `GET /api/tags`，Then 该标签不出现
- Given 标签挂在 2 篇已发布上，Then `article_count=2`
- Given `GET /api/articles?tag={slug}`，Then 只返回该标签的已发布文章

**先写测试：** `api/tests/test_tags.py::test_public_tags_ignore_draft_only`

### US-14 读者能搜索已发布文章

**作为** 读者，**我想** 用关键词搜标题和正文，**以便** 找回旧文。

**PRD：** FR-15  
**验收：**

- Given 已发布标题含「FTS5」，When `GET /api/articles?q=FTS5`，Then 命中该文
- Given 仅草稿正文含该词，When 搜索，Then 不命中
- Given 已发布后撤回，When 再搜原词，Then 不命中

**先写测试：** `api/tests/test_search.py::test_fts_only_published`

### US-15 空搜索与无结果有明确反馈

**作为** 读者，**我想** 知道自己没输入或没有结果，**以便** 换词继续找。

**PRD：** FR-16, FR-17  
**验收：**

- Given 搜索框为空，When 点搜索，Then 不发出 `q=` 请求，输入框提示「输入关键词」
- Given `q=不可能存在的词xyz`，When API 返回 `items=[]`，Then 页面文案「没有找到相关文章」

**先写测试：** `web/src/__tests__/SearchPage.test.tsx`

---

## E5 评论

### US-16 未登录可以看评但不能发

**作为** 读者，**我想** 先看别人怎么说，**以便** 决定要不要登录留言。

**PRD：** FR-20  
**验收：**

- Given 已发布文章有评论，When 未带 `reader_session` 访问详情，Then 评论列表可见
- Given 未登录，When `POST` 评论，Then `401`，页面展示「使用 GitHub 登录」而不是表单提交成功

**先写测试：** `api/tests/test_comments.py::test_anonymous_cannot_post`

### US-17 读者能用 GitHub 登录并回到原文

**作为** 读者，**我想** 用 GitHub 登录后回到正在看的文章，**以便** 马上评论。

**PRD：** FR-21  
**验收：**

- Given `GET /api/auth/github?next=/posts/hello`，Then 302 到 GitHub，且设置 `oauth_state`
- Given 合法 `state` + mock 成功换票，When 打 callback，Then 设置 `reader_session`，302 到 `{PUBLIC_WEB_ORIGIN}/posts/hello`
- Given `next=https://evil.example`，When 回调，Then 回跳 `/` 而不是外链
- Given 错误 `state`，When 回调，Then `400 OAUTH_FAILED`，不设读者 Cookie

**先写测试：** `api/tests/test_oauth.py::test_oauth_callback_rejects_bad_next_and_state`

### US-18 已登录读者评论后立刻可见

**作为** 已登录读者，**我想** 提交后马上看到自己的评论，**以便** 确认发出去了。

**PRD：** FR-22, FR-23, FR-24  
**验收：**

- Given 有效 `reader_session` 与已发布文章，When `POST {"body":"写得清楚"}`，Then `201`，`GET` 列表末尾出现该条，含 `github_login` 与 `github_avatar_url`
- Given `body` 为空或超过 2000 字，When POST，Then `422`
- Given `body` 含 `<script>alert(1)</script>`，When 展示，Then 按纯文本出现，不执行脚本

**先写测试：** `api/tests/test_comments.py::test_reader_can_post_and_see_immediately`

### US-19 作者能删除任意评论

**作为** 作者，**我想** 删掉不当评论，**以便** 讨论区可阅读。

**PRD：** FR-25  
**验收：**

- Given 存在评论 id=1，When 作者 `DELETE /api/admin/comments/1`，Then `204`，再 `GET` 列表无 id=1
- Given 读者会话（非作者），When 调同一 DELETE，Then `401` 或 `404`（读者无该路由权限）
- Given 不存在的 id，When 作者删除，Then `404`

**先写测试：** `api/tests/test_comments.py::test_admin_can_delete_comment`

### US-20 读者能退出 GitHub 登录

**作为** 读者，**我想** 退出登录，**以便** 在公共电脑上离开。

**PRD：** FR-26  
**验收：**

- Given 已登录读者，When `POST /api/auth/github/logout`，Then `reader_session` 清除，`GET /api/auth/github/me` 为 `401`
- Given 同时存在 `admin_session`，When 读者退出，Then 作者会话仍有效

**先写测试：** `api/tests/test_oauth.py::test_reader_logout_does_not_clear_admin`

---

## E6 作者会话

### US-21 作者能用环境变量账号登录后台

**作为** 作者，**我想** 用设定好的用户名密码进入后台，**以便** 写文章。

**PRD：** FR-27  
**验收：**

- Given 正确用户名密码，When `POST /api/auth/admin/login`，Then `200` 且带 `admin_session`，`GET /api/auth/admin/me` 成功
- Given 未登录，When 打开 `/admin/posts`，Then 前端转到 `/admin/login`

**先写测试：** `api/tests/test_admin_auth.py::test_login_sets_cookie`

### US-22 错误密码只有通用提示

**作为** 作者，**我不想** 登录失败时暴露账号是否存在，**以便** 降低被猜账号的风险。

**PRD：** FR-28  
**验收：**

- Given 错误密码或未知用户名，When 登录，Then 皆为 `401 UNAUTHORIZED`，`message` 同为「用户名或密码不正确」
- Given 响应时间，Then 实现使用恒定时间比较密码（测试可只断言文案与状态；代码审阅确认 `secrets.compare_digest`）

**先写测试：** `api/tests/test_admin_auth.py::test_login_same_error_for_bad_user_and_password`

### US-23 作者能退出后台且不影响读者会话

**作为** 作者，**我想** 退出后台，**以便** 结束管理操作。

**PRD：** FR-30  
**验收：**

- Given 作者已登录，When `POST /api/auth/admin/logout`，Then `GET /api/auth/admin/me` 为 `401`，此后写接口均 `401`
- Given 同时有读者 Cookie，When 作者退出，Then `GET /api/auth/github/me` 仍成功

**先写测试：** `api/tests/test_admin_auth.py::test_admin_logout_keeps_reader_session`

---

## E7 部署验收

### US-24 Compose 能跑通主路径（不含真实 GitHub 时用 mock 配置）

**作为** 作者，**我想** `docker compose up` 后在浏览器走完写作与阅读，**以便** 单机部署。

**PRD：** FR-34, FR-35  
**验收：**

- Given 根目录 Compose，When `docker compose config`，Then 服务仅为 `web`、`api`，存在 named volume 或绑定到数据目录
- Given compose 已启动，When 访问 web 端口与 `GET /api/health`，Then 均成功
- Given 用作者账号登录后台发布一篇，When 打开首页，Then 可见该文（浏览器验收，证据截图或步骤记在 Issue）

**先写测试：** 以 `docker compose config` 的静态断言脚本或文档化手工清单为准；API 健康检查复用 `test_health_ok`。

---

## 建议的 Issue 拆分顺序

创建 GitHub Issues 时按依赖，不要并行创建「被阻塞却看不出依赖」的实现任务：

1. US-01 健康检查与仓库骨架  
2. US-21, US-22, US-23 作者会话  
3. US-02 … US-07 文章状态机  
4. US-11 上传  
5. US-12, US-13 标签  
6. US-08, US-09, US-10 公开阅读与关于我  
7. US-14, US-15 搜索  
8. US-16 … US-20 评论与 OAuth  
9. 前端页面对应的 `type:frontend` Issue（可按页面再拆，但仍挂上述 US）  
10. US-24 Compose  

拆 Issue 的完整字段模板见计划；落地后同步 [06-issue-backlog.md](06-issue-backlog.md)（创建 Issues 时再写）。
