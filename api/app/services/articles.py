from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import fts_delete, fts_upsert
from app.errors import AppError
from app.models import Article, Tag
from app.slug import is_valid_slug, slugify


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def excerpt_of(article: Article) -> str | None:
    if article.excerpt:
        return article.excerpt
    text = article.body_md.replace("\n", "")
    return text[:160] if text else ""


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            base = slugify(name)
            if base == "untitled":
                base = f"tag-{abs(hash(name)) % 10**8}"
            slug = base
            suffix = 1
            while db.scalar(select(Tag).where(Tag.slug == slug)):
                suffix += 1
                slug = f"{base}-{suffix}"
            tag = Tag(name=name, slug=slug)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def article_count_hint(db: Session) -> int:
    return int(db.scalar(select(func.count()).select_from(Tag)) or 0)


def ensure_unique_slug(db: Session, slug: str, exclude_id: int | None = None) -> None:
    query = select(Article).where(Article.slug == slug)
    if exclude_id is not None:
        query = query.where(Article.id != exclude_id)
    if db.scalar(query):
        raise AppError(409, "SLUG_CONFLICT", "这个短链接已被占用")


def resolve_slug(db: Session, title: str, explicit: str | None, exclude_id: int | None = None) -> str:
    slug = explicit if explicit is not None else slugify(title)
    if not is_valid_slug(slug):
        raise AppError(422, "VALIDATION_ERROR", "短链接不合法")
    ensure_unique_slug(db, slug, exclude_id)
    return slug


def serialize_admin(article: Article) -> dict:
    return {
        "id": article.id,
        "slug": article.slug,
        "title": article.title,
        "body_md": article.body_md,
        "excerpt": article.excerpt,
        "cover_path": article.cover_path,
        "status": article.status,
        "published_at": article.published_at,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
        "tags": [{"name": tag.name, "slug": tag.slug} for tag in article.tags],
    }


def serialize_public_item(article: Article) -> dict:
    return {
        "slug": article.slug,
        "title": article.title,
        "excerpt": excerpt_of(article),
        "cover_path": article.cover_path,
        "published_at": article.published_at,
        "tags": [{"name": tag.name, "slug": tag.slug} for tag in article.tags],
    }


def serialize_public_detail(article: Article) -> dict:
    return {
        **serialize_public_item(article),
        "body_md": article.body_md,
        "updated_at": article.updated_at,
    }


def load_article(db: Session, article_id: int) -> Article:
    article = db.scalar(
        select(Article).options(selectinload(Article.tags)).where(Article.id == article_id)
    )
    if article is None:
        raise AppError(404, "NOT_FOUND", "文章不存在")
    return article


def create_article(db: Session, data: dict) -> Article:
    now = utcnow()
    slug = resolve_slug(db, data["title"], data.get("slug"))
    article = Article(
        slug=slug,
        title=data["title"],
        body_md=data.get("body_md") or "",
        excerpt=data.get("excerpt"),
        cover_path=data.get("cover_path"),
        status="draft",
        published_at=None,
        created_at=now,
        updated_at=now,
        tags=get_or_create_tags(db, data.get("tag_names") or []),
    )
    db.add(article)
    db.commit()
    return load_article(db, article.id)


def patch_article(db: Session, article_id: int, data: dict) -> Article:
    article = load_article(db, article_id)
    if "title" in data and data["title"] is not None:
        article.title = data["title"]
    if "body_md" in data and data["body_md"] is not None:
        article.body_md = data["body_md"]
    if "excerpt" in data:
        article.excerpt = data["excerpt"]
    if "cover_path" in data:
        article.cover_path = data["cover_path"]
    if "slug" in data and data["slug"] is not None:
        article.slug = resolve_slug(db, article.title, data["slug"], article.id)
    if "tag_names" in data and data["tag_names"] is not None:
        article.tags = get_or_create_tags(db, data["tag_names"])
    article.updated_at = utcnow()
    if article.status == "published":
        fts_upsert(db, article.id, article.title, article.body_md)
    db.commit()
    return load_article(db, article.id)


def publish_article(db: Session, article_id: int) -> Article:
    article = load_article(db, article_id)
    if not article.title.strip():
        raise AppError(422, "VALIDATION_ERROR", "标题不能为空")
    if not is_valid_slug(article.slug):
        raise AppError(422, "VALIDATION_ERROR", "短链接不合法")
    article.status = "published"
    article.published_at = utcnow()
    article.updated_at = article.published_at
    fts_upsert(db, article.id, article.title, article.body_md)
    db.commit()
    return load_article(db, article.id)


def unpublish_article(db: Session, article_id: int) -> Article:
    article = load_article(db, article_id)
    article.status = "draft"
    article.published_at = None
    article.updated_at = utcnow()
    fts_delete(db, article.id)
    db.commit()
    return load_article(db, article.id)


def delete_article(db: Session, article_id: int) -> None:
    article = load_article(db, article_id)
    fts_delete(db, article.id)
    db.delete(article)
    db.commit()
