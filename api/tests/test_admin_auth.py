from fastapi.testclient import TestClient

from app.main import app
from app.session import make_reader_cookie

client = TestClient(app)


def test_login_sets_cookie() -> None:
    response = client.post(
        "/api/auth/admin/login",
        json={"username": "admin", "password": "secret"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert "admin_session" in response.cookies
    me = client.get("/api/auth/admin/me")
    assert me.status_code == 200
    assert me.json()["role"] == "admin"
    assert me.json()["username"] == "admin"


def test_login_same_error_for_bad_user_and_password() -> None:
    bad_user = client.post(
        "/api/auth/admin/login",
        json={"username": "nobody", "password": "secret"},
    )
    bad_pass = client.post(
        "/api/auth/admin/login",
        json={"username": "admin", "password": "nope"},
    )
    assert bad_user.status_code == 401
    assert bad_pass.status_code == 401
    assert bad_user.json()["error"]["code"] == "UNAUTHORIZED"
    assert bad_pass.json()["error"]["code"] == "UNAUTHORIZED"
    assert bad_user.json()["error"]["message"] == "用户名或密码不正确"
    assert bad_pass.json()["error"]["message"] == "用户名或密码不正确"


def test_admin_logout_keeps_reader_session() -> None:
    client.post("/api/auth/admin/login", json={"username": "admin", "password": "secret"})
    client.cookies.set(
        "reader_session",
        make_reader_cookie(github_id=1, login="octocat", avatar_url="https://example.com/a.png"),
    )
    logout = client.post("/api/auth/admin/logout")
    assert logout.status_code == 200
    assert client.get("/api/auth/admin/me").status_code == 401
    reader = client.get("/api/auth/github/me")
    assert reader.status_code == 200
    assert reader.json()["login"] == "octocat"
