"""Health and request id tests."""

from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_ok() -> None:
    response = client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-Id")


def test_readyz_returns_ok() -> None:
    response = client.get("/api/v1/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "ready": True}


def test_request_id_echoed() -> None:
    request_id = "test-request-id"
    response = client.get("/api/v1/healthz", headers={"X-Request-Id": request_id})
    assert response.headers.get("X-Request-Id") == request_id


def test_request_id_generated() -> None:
    response = client.get("/api/v1/healthz")
    request_id = response.headers.get("X-Request-Id")
    assert request_id
    UUID(request_id)
