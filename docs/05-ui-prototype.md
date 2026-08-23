# UI 原型：zw-blog

| 项 | 内容 |
| --- | --- |
| 可点击原型 | [../prototype/index.html](../prototype/index.html) |
| 设计系统 | [../design-system/MASTER.md](../design-system/MASTER.md) |
| 对应 PRD | [01-prd.md](01-prd.md) |

## 1. 对象与一页一事

- **对象：** 一个写技术笔记、也写日常感悟的人（中文为主）。
- **读者打开站点的唯一任务：** 找到一篇想读的文章并读完。
- **作者打开后台的唯一任务：** 把草稿写成可发布的 Markdown。

不是 newsletter、不是作品集英雄区、不是仪表盘。

## 2. 设计系统（相对默认方案的修正）

`ui-ux-pro-max` 给出的默认是「订阅通讯 + Swiss + 粉色 CTA + Caveat/Quicksand」。本产品没有订阅，中文长文也不适合手写英文字。采用其可用部分（内容优先、阅读行宽、表单要有 label），其余按主题重做。

| 角色 | 名称 | Hex | 用途 |
| --- | --- | --- | --- |
| Ground | 图纸灰 | `#DDE3EA` | 整站底，偏冷，避开常见暖米色 |
| Ink | 墨蓝 | `#16202C` | 标题与正文 |
| Mute | 铅灰 | `#4E5D6C` | 元信息、次要导航 |
| Copper | 书签铜 | `#B85C38` | **唯一强调色**：书脊线、当前项、主按钮 |
| Card | 卡片白 | `#F3F6F8` | 编辑区、评论区 |
| Rule | 细线 | `#C5CED6` | 分割 |
| Code | 桌面终端 | `#16202C` / `#D7E3C8` | 代码块 |

**字体**

- 标题：`Noto Serif SC`（中文阅读，克制使用大号）
- 正文 / UI：`IBM Plex Sans` + `Noto Sans SC`
- 代码与日期书脊：`IBM Plex Mono`

**布局**

- 公开站：一条约 62ch 的阅读栏；左侧一条铜线当「夹在本子里的书签」。
- 列表项左侧竖排日期（年 / 月日），像书架书脊，而不是卡片网格。
- 后台：同一色板，去掉书脊，信息更密，方便改稿。

**签名元素（只大胆这一处）**

文章列表与正文左侧的铜书签线 + 竖排日期。其它装饰尽量去掉。

**刻意不用**

- 订阅表单、读者数、粉红 CTA
- 手写英文字 / 暖米色衬线默认套装
- Emoji 当图标
- 全宽无行宽限制的正文

## 3. 原型页清单

| 文件 | 对应 |
| --- | --- |
| `prototype/index.html` | 首页列表、空态可对照文案 |
| `prototype/post.html` | 正文 + 未登录评论 |
| `prototype/post-logged.html` | 已登录读者可发评 |
| `prototype/post-admin.html` | 作者可见删除评论 |
| `prototype/tags.html` / `tag.html` | 标签索引与筛选 |
| `prototype/search.html` | 空提交提示、无结果、有结果（页内切换） |
| `prototype/about.html` | 关于我 |
| `prototype/admin-login.html` | 后台登录（含错误态） |
| `prototype/admin-posts.html` | 后台列表 + 状态筛选 |
| `prototype/admin-edit.html` | Markdown 编辑 + 预览 |
| `prototype/admin-about.html` | 编辑关于我 |

本地预览：在 `prototype/` 下执行 `python -m http.server 4177`，打开 http://127.0.0.1:4177/index.html。  
后台原型登录（仅演示）：用户名 `admin`，密码 `admin`；其它组合会提示「用户名或密码不正确」。

## 4. 文案（界面用词，开发时勿改）

- 导航：日志、标签、搜索、关于
- 空列表：还没有文章
- 文章 404：文章不存在
- 关于空：作者还没有写介绍
- 搜索空提交：输入关键词
- 搜索无结果：没有找到相关文章
- 评论未登录：使用 GitHub 登录
- 后台按钮：保存草稿、发布、撤回为草稿、删除评论
- 登录失败：用户名或密码不正确

## 5. UX 底线（实现时）

- 正文行宽 65–75 字符（中文约 32–40 字）
- 表单必须有可见 label，不能只用 placeholder
- 错误用 `role="alert"`，不能只靠变红
- 对比度 ≥ 4.5:1；键盘可见 focus
- 尊重 `prefers-reduced-motion`
- 点击元素有 `cursor: pointer` 与 150–300ms 颜色过渡，不用放大造成位移
