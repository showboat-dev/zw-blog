from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.deps import require_admin
from app.models import Article
from app.schemas import ArticleCreate, ArticlePatch
from app.services import articles as svc

router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])


@router.post("/articles", status_code=201)
def create_article(body: ArticleCreate, db: Session = Depends(get_db)) -> dict:
    article = svc.create_article(db, body.model_dump())
    return svc.serialize_admin(article)


@router.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)) -> dict:
    return svc.serialize_admin(svc.load_article(db, article_id))


@router.get("/articles")
def list_articles(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict:
    query = select(Article).options(selectinload(Article.tags))
    count_query = select(func.count()).select_from(Article)
    if status:
        query = query.where(Article.status == status)
        count_query = count_query.where(Article.status == status)
    total = int(db.scalar(count_query) or 0)
    items = db.scalars(
        query.order_by(Article.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": [svc.serialize_admin(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.patch("/articles/{article_id}")
def patch_article(
    article_id: int, body: ArticlePatch, db: Session = Depends(get_db)
) -> dict:
    article = svc.patch_article(db, article_id, body.model_dump(exclude_unset=True))
    return svc.serialize_admin(article)


@router.delete("/articles/{article_id}", status_code=204)
def delete_article(article_id: int, db: Session = Depends(get_db)) -> None:
    svc.delete_article(db, article_id)


@router.post("/articles/{article_id}/publish")
def publish_article(article_id: int, db: Session = Depends(get_db)) -> dict:
    return svc.serialize_admin(svc.publish_article(db, article_id))


@router.post("/articles/{article_id}/unpublish")
def unpublish_article(article_id: int, db: Session = Depends(get_db)) -> dict:
    return svc.serialize_admin(svc.unpublish_article(db, article_id))
