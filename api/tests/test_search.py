from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def test_fts_only_published(client: TestClient) -> None:
    login_admin(client)
    published = client.post(
        "/api/admin/articles",
        json={"title": "学习 FTS5", "slug": "fts-pub", "body_md": "hello"},
    )
    draft = client.post(
        "/api/admin/articles",
        json={"title": "草稿", "slug": "fts-draft", "body_md": "FTS5 只在草稿"},
    )
    client.post(f"/api/admin/articles/{published.json()['id']}/publish")
    hits = client.get("/api/articles?q=FTS5")
    assert {item["slug"] for item in hits.json()["items"]} == {"fts-pub"}
    client.post(f"/api/admin/articles/{published.json()['id']}/unpublish")
    after = client.get("/api/articles?q=FTS5")
    assert after.json()["items"] == []
    assert draft.status_code == 201
