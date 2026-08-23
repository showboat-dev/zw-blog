from fastapi.testclient import TestClient
import pytest

from app.session import make_reader_cookie
from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def _published(client: TestClient) -> None:
    login_admin(client)
    created = client.post(
        "/api/admin/articles",
        json={"title": "评", "slug": "cmt", "body_md": "x"},
    )
    client.post(f"/api/admin/articles/{created.json()['id']}/publish")
    client.cookies.pop("admin_session", None)


def test_anonymous_cannot_post(client: TestClient) -> None:
    _published(client)
    listed = client.get("/api/articles/cmt/comments")
    assert listed.status_code == 200
    assert listed.json()["items"] == []
    denied = client.post("/api/articles/cmt/comments", json={"body": "hi"})
    assert denied.status_code == 401


def test_reader_can_post_and_see_immediately(client: TestClient) -> None:
    _published(client)
    client.cookies.set(
        "reader_session",
        make_reader_cookie(9, "octocat", "https://example.com/a.png"),
    )
    empty = client.post("/api/articles/cmt/comments", json={"body": "  "})
    assert empty.status_code == 422
    too_long = client.post("/api/articles/cmt/comments", json={"body": "哈" * 2001})
    assert too_long.status_code == 422
    created = client.post(
        "/api/articles/cmt/comments",
        json={"body": "<script>alert(1)</script>写得清楚"},
    )
    assert created.status_code == 201
    items = client.get("/api/articles/cmt/comments").json()["items"]
    assert items[-1]["github_login"] == "octocat"
    assert items[-1]["body"] == "<script>alert(1)</script>写得清楚"


def test_admin_can_delete_comment(client: TestClient) -> None:
    _published(client)
    client.cookies.set(
        "reader_session",
        make_reader_cookie(9, "octocat", "https://example.com/a.png"),
    )
    created = client.post("/api/articles/cmt/comments", json={"body": "删我"})
    comment_id = created.json()["id"]
    as_reader = client.delete(f"/api/admin/comments/{comment_id}")
    assert as_reader.status_code == 401
    login_admin(client)
    missing = client.delete("/api/admin/comments/99999")
    assert missing.status_code == 404
    deleted = client.delete(f"/api/admin/comments/{comment_id}")
    assert deleted.status_code == 204
    items = client.get("/api/articles/cmt/comments").json()["items"]
    assert all(item["id"] != comment_id for item in items)


def test_delete_article_cascades_comments(client: TestClient) -> None:
    login_admin(client)
    created = client.post("/api/admin/articles", json={"title": "X", "slug": "gone"})
    article_id = created.json()["id"]
    client.post(f"/api/admin/articles/{article_id}/publish")
    client.cookies.set(
        "reader_session",
        make_reader_cookie(9, "octocat", "https://example.com/a.png"),
    )
    client.post("/api/articles/gone/comments", json={"body": "bye"})
    login_admin(client)
    assert client.delete(f"/api/admin/articles/{article_id}").status_code == 204
    assert client.get("/api/articles/gone").status_code == 404
    assert client.get("/api/articles/gone/comments").status_code == 404
