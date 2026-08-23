import secrets

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from app import session
from app.config import settings
from app.deps import require_admin, require_reader
from app.errors import AppError

router = APIRouter()


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


@router.post("/api/auth/github/logout")
def github_logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(session.READER_COOKIE, path="/")
    return {"ok": True}
