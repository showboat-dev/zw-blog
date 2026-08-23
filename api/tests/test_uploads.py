from io import BytesIO

from fastapi.testclient import TestClient
import pytest

from tests.helpers import login_admin, make_client


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    upload_dir = tmp_path / "uploads"
    monkeypatch.setenv("UPLOAD_DIR", str(upload_dir))
    from app.config import settings

    settings.upload_dir = str(upload_dir)
    yield from make_client(str(tmp_path / "test.db"))


def test_upload_rejects_bad_type_and_anonymous(client: TestClient) -> None:
    files = {"file": ("x.exe", BytesIO(b"mz"), "application/octet-stream")}
    assert client.post("/api/admin/uploads", files=files).status_code == 401
    login_admin(client)
    bad = client.post("/api/admin/uploads", files=files)
    assert bad.status_code == 422
    huge = {"file": ("big.jpg", BytesIO(b"x" * 5_242_881), "image/jpeg")}
    assert client.post("/api/admin/uploads", files=huge).status_code == 422
    ok = client.post(
        "/api/admin/uploads",
        files={"file": ("pic.jpg", BytesIO(b"\xff\xd8\xff" + b"x" * 20), "image/jpeg")},
    )
    assert ok.status_code == 201
    assert ok.json()["url"].startswith("/api/uploads/")
    stored = client.get(ok.json()["url"])
    assert stored.status_code == 200
