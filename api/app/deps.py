from fastapi import Cookie

from app import session
from app.errors import AppError


def require_admin(admin_session: str | None = Cookie(default=None)) -> dict:
    payload = session.unsign(admin_session or "", session.ADMIN_MAX_AGE)
    if not payload or payload.get("role") != "admin":
        raise AppError(401, "UNAUTHORIZED", "未登录")
    return payload


def optional_reader(reader_session: str | None = Cookie(default=None)) -> dict | None:
    return session.unsign(reader_session or "", session.READER_MAX_AGE)


def require_reader(reader_session: str | None = Cookie(default=None)) -> dict:
    payload = session.unsign(reader_session or "", session.READER_MAX_AGE)
    if not payload or "github_id" not in payload:
        raise AppError(401, "UNAUTHORIZED", "请先使用 GitHub 登录")
    return payload
