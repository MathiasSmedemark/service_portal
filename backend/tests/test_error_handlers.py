"""Tests for API error handlers."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_error_shape(response, expected_code: str) -> None:
    assert "X-Request-Id" in response.headers
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == expected_code
    assert isinstance(body["error"]["message"], str)
    assert body["error"]["request_id"] == response.headers["X-Request-Id"]


def test_not_found_uses_standard_error_shape() -> None:
    response = client.get("/api/v1/unknown-route")

    assert response.status_code == 404
    _assert_error_shape(response, "not_found")


def test_validation_error_uses_standard_error_shape() -> None:
    response = client.get("/api/v1/platforms", params={"limit": "nope"})

    assert response.status_code == 422
    _assert_error_shape(response, "validation_error")
