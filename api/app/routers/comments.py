from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin, require_reader
from app.errors import AppError
from app.models import Article, Comment
from app.services.articles import utcnow

router = APIRouter()


class CommentBody(BaseModel):
    body: str


def _published_article(db: Session, slug: str) -> Article:
    article = db.scalar(
        select(Article).where(Article.slug == slug, Article.status == "published")
    )
    if article is None:
        raise AppError(404, "NOT_FOUND", "文章不存在")
    return article


@router.get("/api/articles/{slug}/comments")
def list_comments(slug: str, db: Session = Depends(get_db)) -> dict:
    article = _published_article(db, slug)
    items = db.scalars(
        select(Comment)
        .where(Comment.article_id == article.id)
        .order_by(Comment.created_at.asc())
    ).all()
    return {
        "items": [
            {
                "id": item.id,
                "github_login": item.github_login,
                "github_avatar_url": item.github_avatar_url,
                "body": item.body,
                "created_at": item.created_at,
            }
            for item in items
        ]
    }


@router.post("/api/articles/{slug}/comments", status_code=201)
def create_comment(
    slug: str,
    body: CommentBody,
    db: Session = Depends(get_db),
    reader: dict = Depends(require_reader),
) -> dict:
    text = body.body.strip()
    if not text or len(body.body) > 2000:
        raise AppError(422, "VALIDATION_ERROR", "评论长度不合法")
    article = _published_article(db, slug)
    comment = Comment(
        article_id=article.id,
        github_id=int(reader["github_id"]),
        github_login=reader["login"],
        github_avatar_url=reader["avatar_url"],
        body=body.body,
        created_at=utcnow(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "github_login": comment.github_login,
        "github_avatar_url": comment.github_avatar_url,
        "body": comment.body,
        "created_at": comment.created_at,
    }


@router.delete("/api/admin/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _admin: dict = Depends(require_admin),
) -> None:
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise AppError(404, "NOT_FOUND", "评论不存在")
    db.delete(comment)
    db.commit()
