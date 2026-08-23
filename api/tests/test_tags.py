from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def test_tag_names_create_or_reuse(client: TestClient) -> None:
    login_admin(client)
    first = client.post(
        "/api/admin/articles",
        json={"title": "A", "slug": "a1", "tag_names": ["技术", "随笔"]},
    )
    assert first.status_code == 201
    names = {tag["name"] for tag in first.json()["tags"]}
    assert names == {"技术", "随笔"}
    second = client.post(
        "/api/admin/articles",
        json={"title": "B", "slug": "b1", "tag_names": ["技术"]},
    )
    assert {tag["name"] for tag in second.json()["tags"]} == {"技术"}
    client.post(f"/api/admin/articles/{first.json()['id']}/publish")
    detail = client.get("/api/articles/a1")
    assert {"name", "slug"} <= set(detail.json()["tags"][0])


def test_public_tags_ignore_draft_only(client: TestClient) -> None:
    login_admin(client)
    draft = client.post(
        "/api/admin/articles",
        json={"title": "D", "slug": "draft-tag", "tag_names": ["仅草稿"]},
    )
    pub1 = client.post(
        "/api/admin/articles",
        json={"title": "P1", "slug": "p-tag-1", "tag_names": ["技术"]},
    )
    pub2 = client.post(
        "/api/admin/articles",
        json={"title": "P2", "slug": "p-tag-2", "tag_names": ["技术"]},
    )
    client.post(f"/api/admin/articles/{pub1.json()['id']}/publish")
    client.post(f"/api/admin/articles/{pub2.json()['id']}/publish")
    tags = client.get("/api/tags")
    items = {item["name"]: item["article_count"] for item in tags.json()["items"]}
    assert "仅草稿" not in items
    assert items["技术"] == 2
    filtered = client.get("/api/articles?tag=" + tags.json()["items"][0]["slug"])
    assert {item["slug"] for item in filtered.json()["items"]} == {"p-tag-1", "p-tag-2"}
    assert draft.status_code == 201
