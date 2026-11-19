import os

os.environ["API_KEY"] = "test-key"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_and_headers():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers["x-content-type-options"] == "nosniff"


def test_requires_key():
    assert client.post("/items", json={"name": "a", "price": 1}).status_code == 401
    r = client.post("/items", json={"name": "a", "price": 1}, headers={"X-API-Key": "test-key"})
    assert r.status_code == 201
