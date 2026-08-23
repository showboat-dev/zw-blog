from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path) -> TestClient:
    yield from make_client(str(tmp_path / "test.db"))


def test_about_empty_and_update(client: TestClient) -> None:
    empty = client.get("/api/about")
    assert empty.status_code == 200
    assert empty.json() == {"body_md": ""}
    denied = client.put("/api/admin/about", json={"body_md": "hi"})
    assert denied.status_code == 401
    login_admin(client)
    updated = client.put("/api/admin/about", json={"body_md": "你好"})
    assert updated.status_code == 200
    assert client.get("/api/about").json()["body_md"] == "你好"
