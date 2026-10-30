#!/usr/bin/env python3
"""Seed the database with sample articles and tags."""

from datetime import datetime

from app import db as database
from app.models import Article, Tag
from app.slug import slugify


def seed() -> None:
    """Add sample articles with tags to demonstrate the blog."""
    database.init_db()
    assert database.SessionLocal is not None
    session = database.SessionLocal()

    try:
        # Check if articles already exist
        existing_count = session.query(Article).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} article(s). Skipping seed.")
            return

        # Create tags
        tech_tag = Tag(name="技术", slug="tech")
        essay_tag = Tag(name="随笔", slug="essay")
        tutorial_tag = Tag(name="教程", slug="tutorial")

        # Sample Article 1: Technical post
        article1 = Article(
            slug="welcome-to-my-blog",
            title="欢迎来到我的博客",
            body_md="""# 欢迎

这是我的个人博客，用来分享技术文章和生活感悟。

## 技术栈

这个博客使用了以下技术：

- **前端**: React + Vite
- **后端**: FastAPI + SQLAlchemy
- **数据库**: SQLite
- **部署**: Docker Compose

## 特性

- ✅ Markdown 支持
- ✅ 代码高亮
- ✅ 标签分类
- ✅ 全文搜索
- ✅ GitHub 评论登录

欢迎留言交流！
""",
            excerpt="博客介绍与技术栈说明",
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=[tech_tag, tutorial_tag],
        )

        # Sample Article 2: Code tutorial
        article2 = Article(
            slug="python-fastapi-quick-start",
            title="FastAPI 快速入门",
            body_md="""# FastAPI 快速入门

FastAPI 是一个现代、快速的 Python Web 框架。

## 安装

```bash
pip install fastapi uvicorn
```

## 第一个 API

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

## 运行服务器

```bash
uvicorn main:app --reload
```

访问 `http://localhost:8000/docs` 可以看到自动生成的 API 文档。

## 特点

1. **快速**: 性能可媲美 NodeJS 和 Go
2. **易用**: 减少代码重复，提高开发效率
3. **类型检查**: 基于 Python 类型提示
4. **自动文档**: 自动生成交互式 API 文档

试试看吧！
""",
            excerpt="使用 FastAPI 构建你的第一个 API",
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=[tech_tag, tutorial_tag],
        )

        # Sample Article 3: Essay
        article3 = Article(
            slug="on-learning",
            title="关于学习这件事",
            body_md="""最近在思考学习的本质。

学习不是填鸭式的灌输，而是主动的探索和思考。就像编程一样，看再多教程，不如自己动手写一遍代码。

## 学习的三个阶段

1. **模仿**: 从复制优秀的代码开始
2. **理解**: 弄懂为什么要这样写
3. **创造**: 能够独立解决新问题

编程如此，学习其他事物也是如此。

保持好奇心，保持探索的热情。
""",
            excerpt="一些关于学习的思考",
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=[essay_tag],
        )

        # Sample Article 4: Draft (not published)
        article4 = Article(
            slug="react-hooks-draft",
            title="React Hooks 深入解析（草稿）",
            body_md="""# React Hooks 深入解析

这是一篇正在撰写中的文章...

## useState

待补充...

## useEffect

待补充...
""",
            excerpt="正在撰写的 React Hooks 教程",
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=[tech_tag],
        )

        session.add_all([tech_tag, essay_tag, tutorial_tag])
        session.add_all([article1, article2, article3, article4])

        # Update FTS5 for published articles
        for article in [article1, article2, article3]:
            database.fts_upsert(session, article.id, article.title, article.body_md)

        session.commit()

        published_count = (
            session.query(Article).filter(Article.status == "published").count()
        )
        draft_count = session.query(Article).filter(Article.status == "draft").count()
        tags_count = session.query(Tag).count()

        print(f"✅ Seed successful!")
        print(f"   Created {published_count} published articles")
        print(f"   Created {draft_count} draft article(s)")
        print(f"   Created {tags_count} tags")

    except Exception as e:
        session.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
