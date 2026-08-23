from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Article, Tag

router = APIRouter()


@router.get("/api/tags")
def list_tags(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(Tag.name, Tag.slug, func.count(Article.id))
        .join(Tag.articles)
        .where(Article.status == "published")
        .group_by(Tag.id)
        .having(func.count(Article.id) > 0)
        .order_by(Tag.name)
    ).all()
    return {
        "items": [
            {"name": name, "slug": slug, "article_count": count}
            for name, slug, count in rows
        ]
    }
