"""Tests for platform endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_platforms_returns_items() -> None:
    response = client.get("/api/v1/platforms")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("items"), list)
    assert payload["total"] >= len(payload["items"])


def test_get_platform_by_id() -> None:
    response = client.get("/api/v1/platforms")
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No platforms available to validate detail endpoint")

    platform_id = items[0]["id"]
    detail_response = client.get(f"/api/v1/platforms/{platform_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == platform_id


def test_get_platform_missing_returns_404() -> None:
    response = client.get("/api/v1/platforms/platform-does-not-exist")

    assert response.status_code == 404
