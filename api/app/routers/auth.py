import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, Depends, Query, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app import session
from app.config import settings
from app.deps import require_admin, require_reader
from app.errors import AppError

router = APIRouter()


def safe_next(next_path: str | None) -> str:
    if (
        next_path
        and next_path.startswith("/")
        and not next_path.startswith("//")
        and "://" not in next_path
    ):
        return next_path
    return "/"


def exchange_github_code(code: str) -> dict:
    token_resp = httpx.post(
        "https://github.com/login/oauth/access_token",
        json={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
        },
        headers={"Accept": "application/json"},
        timeout=10,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise AppError(400, "OAUTH_FAILED", "GitHub 登录失败")
    user_resp = httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    user_resp.raise_for_status()
    user = user_resp.json()
    if "id" not in user or "login" not in user:
        raise AppError(400, "OAUTH_FAILED", "GitHub 登录失败")
    return {
        "id": user["id"],
        "login": user["login"],
        "avatar_url": user.get("avatar_url") or "",
    }


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/api/auth/admin/login")
def admin_login(body: LoginBody, response: Response) -> dict[str, bool]:
    user_ok = secrets.compare_digest(body.username, settings.admin_username)
    pass_ok = secrets.compare_digest(body.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise AppError(401, "UNAUTHORIZED", "用户名或密码不正确")
    response.set_cookie(
        session.ADMIN_COOKIE,
        session.make_admin_cookie(body.username),
        **session.cookie_kwargs(session.ADMIN_MAX_AGE),
    )
    return {"ok": True}


@router.post("/api/auth/admin/logout")
def admin_logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(session.ADMIN_COOKIE, path="/")
    return {"ok": True}


@router.get("/api/auth/admin/me")
def admin_me(admin: dict = Depends(require_admin)) -> dict:
    return {"role": "admin", "username": admin["username"]}


@router.get("/api/auth/github/me")
def github_me(reader: dict = Depends(require_reader)) -> dict:
    return {
        "github_id": reader["github_id"],
        "login": reader["login"],
        "avatar_url": reader["avatar_url"],
    }


@router.get("/api/auth/github")
def github_login(next: str | None = Query(default="/")) -> RedirectResponse:
    state = secrets.token_urlsafe(24)
    params = urlencode(
        {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_oauth_callback_url,
            "scope": "read:user",
            "state": state,
        }
    )
    response = RedirectResponse(
        f"https://github.com/login/oauth/authorize?{params}",
        status_code=302,
    )
    response.set_cookie(
        session.OAUTH_STATE_COOKIE,
        state,
        **session.cookie_kwargs(session.OAUTH_STATE_MAX_AGE),
    )
    response.set_cookie(
        "oauth_next",
        safe_next(next),
        **session.cookie_kwargs(session.OAUTH_STATE_MAX_AGE),
    )
    return response


@router.get("/api/auth/github/callback")
def github_callback(
    code: str | None = None,
    state: str | None = None,
    oauth_state: str | None = Cookie(default=None),
    oauth_next: str | None = Cookie(default=None),
) -> RedirectResponse:
    if not code or not state or not oauth_state or state != oauth_state:
        raise AppError(400, "OAUTH_FAILED", "GitHub 登录失败")
    user = exchange_github_code(code)
    target = settings.public_web_origin.rstrip("/") + safe_next(oauth_next)
    response = RedirectResponse(target, status_code=302)
    response.set_cookie(
        session.READER_COOKIE,
        session.make_reader_cookie(int(user["id"]), user["login"], user["avatar_url"]),
        **session.cookie_kwargs(session.READER_MAX_AGE),
    )
    response.delete_cookie(session.OAUTH_STATE_COOKIE, path="/")
    response.delete_cookie("oauth_next", path="/")
    return response


@router.post("/api/auth/github/logout")
def github_logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(session.READER_COOKIE, path="/")
    response.set_cookie(
        session.READER_COOKIE,
        "",
        max_age=0,
        path="/",
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}
