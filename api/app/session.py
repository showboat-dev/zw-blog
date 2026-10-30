from typing import Any

from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.config import settings

ADMIN_COOKIE = "admin_session"
READER_COOKIE = "reader_session"
OAUTH_STATE_COOKIE = "oauth_state"

ADMIN_MAX_AGE = 7 * 24 * 3600
READER_MAX_AGE = 30 * 24 * 3600
OAUTH_STATE_MAX_AGE = 5 * 60


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.session_secret, salt="zw-blog-session")


def sign(payload: dict[str, Any]) -> str:
    return _serializer().dumps(payload)


def unsign(token: str, max_age: int) -> dict[str, Any] | None:
    try:
        data = _serializer().loads(token, max_age=max_age)
    except BadSignature:
        return None
    if not isinstance(data, dict):
        return None
    return data


def make_admin_cookie(username: str) -> str:
    return sign({"role": "admin", "username": username})


def make_reader_cookie(github_id: int, login: str, avatar_url: str) -> str:
    return sign(
        {"github_id": github_id, "login": login, "avatar_url": avatar_url}
    )


def cookie_kwargs(max_age: int) -> dict[str, Any]:
    return {
        "httponly": True,
        "samesite": "none" if settings.cookie_secure else "lax",
        "secure": settings.cookie_secure,
        "path": "/",
        "max_age": max_age,
    }
