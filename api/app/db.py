from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import AboutPage, Base

_engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def _sync_url(url: str) -> str:
    return url.replace("sqlite+aiosqlite://", "sqlite://")


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("database is not initialized")
    return _engine


def init_db(url: str | None = None) -> Engine:
    global _engine, SessionLocal
    database_url = _sync_url(url or settings.database_url)
    if database_url.startswith("sqlite:///"):
        db_file = database_url.removeprefix("sqlite:///")
        if db_file and db_file != ":memory:":
            Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _engine = create_engine(database_url, connect_args=connect_args)
    if database_url.startswith("sqlite"):

        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(_engine)
    with _engine.begin() as conn:
        # Use unicode61 for FTS; short queries fall back to LIKE in search logic
        conn.execute(
            text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts "
                "USING fts5(title, body_md, article_id UNINDEXED, tokenize='unicode61 remove_diacritics 0')"
            )
        )
        if conn.execute(text("SELECT COUNT(*) FROM about_page")).scalar() == 0:
            conn.execute(
                text(
                    "INSERT INTO about_page (id, body_md, updated_at) "
                    "VALUES (1, '', CURRENT_TIMESTAMP)"
                )
            )
    return _engine


def get_db() -> Iterator[Session]:
    if SessionLocal is None:
        init_db()
    assert SessionLocal is not None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fts_upsert(db: Session, article_id: int, title: str, body_md: str) -> None:
    db.execute(text("DELETE FROM articles_fts WHERE article_id = :id"), {"id": article_id})
    db.execute(
        text(
            "INSERT INTO articles_fts (title, body_md, article_id) "
            "VALUES (:title, :body, :id)"
        ),
        {"title": title, "body": body_md, "id": article_id},
    )


def fts_delete(db: Session, article_id: int) -> None:
    db.execute(text("DELETE FROM articles_fts WHERE article_id = :id"), {"id": article_id})


# Keep AboutPage imported so metadata includes it at init.
_ = AboutPage
