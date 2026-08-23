from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def test_create_draft_requires_admin(client: TestClient) -> None:
    response = client.post("/api/admin/articles", json={"title": "草稿"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_create_draft_not_listed_publicly(client: TestClient) -> None:
    login_admin(client)
    created = client.post("/api/admin/articles", json={"title": "仅草稿", "slug": "only-draft"})
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "draft"
    assert body["published_at"] is None
    listed = client.get("/api/articles")
    assert listed.status_code == 200
    assert all(item["slug"] != "only-draft" for item in listed.json()["items"])


def test_publish_draft_appears_in_public_list(client: TestClient) -> None:
    login_admin(client)
    created = client.post(
        "/api/admin/articles",
        json={"title": "可发布", "slug": "can-publish", "body_md": "正文"},
    )
    article_id = created.json()["id"]
    empty_title = client.post("/api/admin/articles", json={"title": "x", "slug": "empty-title"})
    client.patch(f"/api/admin/articles/{empty_title.json()['id']}", json={"title": ""})
    rejected = client.post(f"/api/admin/articles/{empty_title.json()['id']}/publish")
    assert rejected.status_code == 422
    assert rejected.json()["error"]["code"] == "VALIDATION_ERROR"

    published = client.post(f"/api/admin/articles/{article_id}/publish")
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert published.json()["published_at"]
    listed = client.get("/api/articles")
    assert listed.json()["items"][0]["slug"] == "can-publish"


def test_unpublish_hides_from_public(client: TestClient) -> None:
    login_admin(client)
    created = client.post(
        "/api/admin/articles",
        json={"title": "撤回", "slug": "to-unpublish"},
    )
    article_id = created.json()["id"]
    client.post(f"/api/admin/articles/{article_id}/publish")
    hidden = client.post(f"/api/admin/articles/{article_id}/unpublish")
    assert hidden.status_code == 200
    assert hidden.json()["status"] == "draft"
    assert hidden.json()["published_at"] is None
    assert client.get("/api/articles/to-unpublish").status_code == 404
    again = client.post(f"/api/admin/articles/{article_id}/publish")
    assert again.json()["published_at"]


def test_slug_conflict_returns_409(client: TestClient) -> None:
    login_admin(client)
    client.post("/api/admin/articles", json={"title": "A", "slug": "taken"})
    other = client.post("/api/admin/articles", json={"title": "B", "slug": "other"})
    conflict = client.patch(
        f"/api/admin/articles/{other.json()['id']}",
        json={"slug": "taken"},
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "SLUG_CONFLICT"
    invalid = client.patch(
        f"/api/admin/articles/{other.json()['id']}",
        json={"slug": "Bad Slug"},
    )
    assert invalid.status_code == 422


def test_admin_list_filter_by_status(client: TestClient) -> None:
    login_admin(client)
    draft = client.post("/api/admin/articles", json={"title": "D", "slug": "d1"})
    pub = client.post("/api/admin/articles", json={"title": "P", "slug": "p1"})
    client.post(f"/api/admin/articles/{pub.json()['id']}/publish")
    drafts = client.get("/api/admin/articles?status=draft")
    pubs = client.get("/api/admin/articles?status=published")
    all_items = client.get("/api/admin/articles")
    assert {item["slug"] for item in drafts.json()["items"]} == {"d1"}
    assert {item["slug"] for item in pubs.json()["items"]} == {"p1"}
    slugs = {item["slug"] for item in all_items.json()["items"]}
    assert slugs == {"d1", "p1"}
    assert "page" in all_items.json()
    assert draft.status_code == 201
