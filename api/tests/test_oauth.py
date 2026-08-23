from fastapi.testclient import TestClient
import pytest

from app.session import make_admin_cookie
from tests.helpers import make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def test_oauth_callback_rejects_bad_next_and_state(client: TestClient, monkeypatch) -> None:
    start = client.get("/api/auth/github?next=/posts/hello", follow_redirects=False)
    assert start.status_code == 302
    assert "github.com" in start.headers["location"]
    assert "oauth_state" in start.cookies

    failed = client.get(
        "/api/auth/github/callback?code=abc&state=not-the-state",
        follow_redirects=False,
    )
    assert failed.status_code == 400
    assert failed.json()["error"]["code"] == "OAUTH_FAILED"

    def fake_exchange(_code: str) -> dict:
        return {"id": 7, "login": "octocat", "avatar_url": "https://example.com/a.png"}

    monkeypatch.setattr("app.routers.auth.exchange_github_code", fake_exchange)
    start = client.get("/api/auth/github?next=https://evil.example", follow_redirects=False)
    state = start.cookies["oauth_state"]
    callback = client.get(
        f"/api/auth/github/callback?code=ok&state={state}",
        follow_redirects=False,
    )
    assert callback.status_code == 302
    assert callback.headers["location"].endswith("/")
    assert "reader_session" in callback.cookies


def test_reader_logout_does_not_clear_admin(client: TestClient) -> None:
    client.cookies.set("admin_session", make_admin_cookie("admin"))
    start = client.get("/api/auth/github?next=/posts/hello", follow_redirects=False)
    from app.session import make_reader_cookie

    client.cookies.set(
        "reader_session",
        make_reader_cookie(1, "octocat", "https://example.com/a.png"),
        path="/",
    )
    assert client.get("/api/auth/github/me").status_code == 200
    logout = client.post("/api/auth/github/logout")
    assert logout.status_code == 200
    set_cookie = logout.headers.get("set-cookie", "").lower()
    assert "reader_session=" in set_cookie
    assert "max-age=0" in set_cookie
    client.cookies.delete("reader_session")
    assert client.get("/api/auth/github/me").status_code == 401
    assert client.get("/api/auth/admin/me").status_code == 200
    assert start.status_code == 302
