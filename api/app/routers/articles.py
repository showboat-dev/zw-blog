from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.errors import AppError
from app.models import Article, Tag
from app.services import articles as svc

router = APIRouter()


def _published_query():
    return select(Article).options(selectinload(Article.tags)).where(Article.status == "published")


@router.get("/api/articles")
def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    tag: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = _published_query()
    count = select(func.count()).select_from(Article).where(Article.status == "published")
    if tag:
        query = query.join(Article.tags).where(Tag.slug == tag)
        count = (
            select(func.count())
            .select_from(Article)
            .join(Article.tags)
            .where(Article.status == "published", Tag.slug == tag)
        )
    if q and q.strip():
        search_term = q.strip()
        # For short queries (< 3 chars), FTS won't match well, so use SQL LIKE instead
        if len(search_term) < 3:
            # Fallback to LIKE search for very short queries
            like_pattern = f"%{search_term}%"
            query = query.where(
                (Article.title.like(like_pattern)) | (Article.body_md.like(like_pattern))
            )
            count = count.where(
                (Article.title.like(like_pattern)) | (Article.body_md.like(like_pattern))
            )
        else:
            # Use FTS for longer queries
            ids = [
                row[0]
                for row in db.execute(
                    text("SELECT article_id FROM articles_fts WHERE articles_fts MATCH :q"),
                    {"q": search_term},
                )
            ]
            query = query.where(Article.id.in_(ids or [-1]))
            count = count.where(Article.id.in_(ids or [-1]))
    total = int(db.scalar(count) or 0)
    items = db.scalars(
        query.order_by(Article.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": [svc.serialize_public_item(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/api/articles/{slug}")
def get_article(slug: str, db: Session = Depends(get_db)) -> dict:
    article = db.scalar(
        _published_query().where(Article.slug == slug)
    )
    if article is None:
        raise AppError(404, "NOT_FOUND", "文章不存在")
    return svc.serialize_public_detail(article)
