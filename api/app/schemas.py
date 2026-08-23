from datetime import datetime

from pydantic import BaseModel, Field


class TagOut(BaseModel):
    name: str
    slug: str


class ArticleListItem(BaseModel):
    slug: str
    title: str
    excerpt: str | None
    cover_path: str | None
    published_at: datetime | None
    tags: list[TagOut]


class ArticlePublic(ArticleListItem):
    body_md: str
    updated_at: datetime


class ArticleAdmin(BaseModel):
    id: int
    slug: str
    title: str
    body_md: str
    excerpt: str | None
    cover_path: str | None
    status: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut]


class ArticleCreate(BaseModel):
    title: str
    body_md: str = ""
    excerpt: str | None = None
    slug: str | None = None
    cover_path: str | None = None
    tag_names: list[str] = Field(default_factory=list)


class ArticlePatch(BaseModel):
    title: str | None = None
    body_md: str | None = None
    excerpt: str | None = None
    slug: str | None = None
    cover_path: str | None = None
    tag_names: list[str] | None = None


class Page(BaseModel):
    items: list
    page: int
    page_size: int
    total: int
