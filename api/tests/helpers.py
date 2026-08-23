from collections.abc import Iterator

from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app


def make_client(db_path: str) -> Iterator[TestClient]:
    init_db("sqlite:///" + str(db_path).replace("\\", "/"))
    with TestClient(app) as client:
        yield client


def login_admin(client: TestClient) -> None:
    response = client.post(
        "/api/auth/admin/login",
        json={"username": "admin", "password": "secret"},
    )
    assert response.status_code == 200
