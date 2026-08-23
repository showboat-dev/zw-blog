from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def _publish(client: TestClient, title: str, slug: str, body: str = "body") -> dict:
    login_admin(client)
    created = client.post(
        "/api/admin/articles",
        json={"title": title, "slug": slug, "body_md": body},
    )
    client.post(f"/api/admin/articles/{created.json()['id']}/publish")
    return created.json()


def test_draft_slug_is_not_found(client: TestClient) -> None:
    login_admin(client)
    client.post(
        "/api/admin/articles",
        json={"title": "秘密草稿标题", "slug": "secret-draft"},
    )
    response = client.get("/api/articles/secret-draft")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "秘密草稿标题" not in response.text


def test_public_list_pagination_and_order(client: TestClient) -> None:
    login_admin(client)
    for index in range(11):
        created = client.post(
            "/api/admin/articles",
            json={"title": f"第{index}篇", "slug": f"p-{index}", "body_md": "很长的正文" * 20},
        )
        client.post(f"/api/admin/articles/{created.json()['id']}/publish")
    page = client.get("/api/articles?page=1&page_size=10")
    data = page.json()
    assert data["total"] == 11
    assert len(data["items"]) == 10
    assert data["items"][0]["slug"] == "p-10"
    assert "body_md" not in data["items"][0]
    assert {"title", "excerpt", "published_at", "tags"} <= set(data["items"][0])


def test_public_detail_returns_body_md(client: TestClient) -> None:
    _publish(client, "详情", "detail-slug", "完整正文")
    response = client.get("/api/articles/detail-slug")
    assert response.status_code == 200
    assert response.json()["body_md"] == "完整正文"
    assert response.json()["title"] == "详情"
    assert client.get("/api/articles/missing").status_code == 404
