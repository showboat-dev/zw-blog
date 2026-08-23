# Issue backlog（与 GitHub 同步）

仓库：https://github.com/showboat-dev/zw-blog/issues
Milestone：v1

| Issue | Key | 标题 |
| --- | --- | --- |
| [#1](https://github.com/showboat-dev/zw-blog/issues/1) | `US-01` | [US-01] 健康检查与仓库骨架 |
| [#2](https://github.com/showboat-dev/zw-blog/issues/2) | `US-21` | [US-21] 作者能用环境变量账号登录后台 |
| [#3](https://github.com/showboat-dev/zw-blog/issues/3) | `US-22` | [US-22] 登录失败只返回通用提示 |
| [#4](https://github.com/showboat-dev/zw-blog/issues/4) | `US-23` | [US-23] 作者退出后台且不影响读者会话 |
| [#5](https://github.com/showboat-dev/zw-blog/issues/5) | `US-02` | [US-02] 作者能创建草稿且对外不可见 |
| [#6](https://github.com/showboat-dev/zw-blog/issues/6) | `US-03` | [US-03] 作者能把草稿改为已发布 |
| [#7](https://github.com/showboat-dev/zw-blog/issues/7) | `US-04` | [US-04] 作者能撤回已发布文章 |
| [#8](https://github.com/showboat-dev/zw-blog/issues/8) | `US-05` | [US-05] 作者能编辑文章并处理 slug 冲突 |
| [#9](https://github.com/showboat-dev/zw-blog/issues/9) | `US-07` | [US-07] 后台文章列表能按状态筛选 |
| [#10](https://github.com/showboat-dev/zw-blog/issues/10) | `US-11` | [US-11] 作者能上传配图 |
| [#11](https://github.com/showboat-dev/zw-blog/issues/11) | `US-12` | [US-12] 写文章时能创建或复用标签 |
| [#12](https://github.com/showboat-dev/zw-blog/issues/12) | `US-13` | [US-13] 读者能浏览标签及其已发布文章 |
| [#13](https://github.com/showboat-dev/zw-blog/issues/13) | `US-08` | [US-08] 公开文章分页列表 API |
| [#14](https://github.com/showboat-dev/zw-blog/issues/14) | `US-09` | [US-09] 公开文章详情返回 Markdown |
| [#15](https://github.com/showboat-dev/zw-blog/issues/15) | `US-10` | [US-10] 关于我读写 API |
| [#16](https://github.com/showboat-dev/zw-blog/issues/16) | `US-14` | [US-14] 搜索只命中已发布文章 |
| [#17](https://github.com/showboat-dev/zw-blog/issues/17) | `US-16` | [US-16] 未登录可以看评但不能发 |
| [#18](https://github.com/showboat-dev/zw-blog/issues/18) | `US-17` | [US-17] GitHub OAuth 登录并安全回跳原文 |
| [#19](https://github.com/showboat-dev/zw-blog/issues/19) | `US-18` | [US-18] 已登录读者评论后立刻可见 |
| [#20](https://github.com/showboat-dev/zw-blog/issues/20) | `US-06` | [US-06] 删除文章时级联删除评论 |
| [#21](https://github.com/showboat-dev/zw-blog/issues/21) | `US-19` | [US-19] 作者能删除任意评论 |
| [#22](https://github.com/showboat-dev/zw-blog/issues/22) | `US-20` | [US-20] 读者退出 GitHub 不影响作者会话 |
| [#23](https://github.com/showboat-dev/zw-blog/issues/23) | `US-08-FE` | [US-08] 首页文章列表页 |
| [#24](https://github.com/showboat-dev/zw-blog/issues/24) | `US-09-FE` | [US-09] 文章详情页与 Markdown 消毒渲染 |
| [#25](https://github.com/showboat-dev/zw-blog/issues/25) | `US-10-FE` | [US-10] 关于页空态与 Markdown |
| [#26](https://github.com/showboat-dev/zw-blog/issues/26) | `US-13-FE` | [US-13] 标签索引页与标签文章页 |
| [#27](https://github.com/showboat-dev/zw-blog/issues/27) | `US-15` | [US-15] 搜索页空输入与无结果 |
| [#28](https://github.com/showboat-dev/zw-blog/issues/28) | `US-18-FE` | [US-16][US-18][US-19] 文章页评论区 |
| [#29](https://github.com/showboat-dev/zw-blog/issues/29) | `US-21-FE` | [US-21] 后台登录页 |
| [#30](https://github.com/showboat-dev/zw-blog/issues/30) | `US-07-FE` | [US-07] 后台文章列表与状态筛选 |
| [#31](https://github.com/showboat-dev/zw-blog/issues/31) | `US-05-FE` | [US-02][US-03][US-05] 后台 Markdown 编辑器 |
| [#32](https://github.com/showboat-dev/zw-blog/issues/32) | `US-10-ADMIN-FE` | [US-10] 后台编辑关于我 |
| [#33](https://github.com/showboat-dev/zw-blog/issues/33) | `US-24` | [US-24] Docker Compose 主路径验收 |

建议实现顺序：先 `US-01`，再作者会话，再文章状态机，再标签/搜索/关于我，再 OAuth 评论，最后前端页与 `US-24`。
