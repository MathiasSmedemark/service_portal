"""Tests for the /me endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_me_returns_forwarded_identity(monkeypatch) -> None:
    monkeypatch.delenv("DEV_USER", raising=False)
    monkeypatch.delenv("DEV_EMAIL", raising=False)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)

    headers = {
        "X-Forwarded-User": "alice",
        "X-Forwarded-Email": "alice@example.com",
        "X-Forwarded-Preferred-Username": "alicep",
    }
    response = client.get("/api/v1/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["preferred_username"] == "alicep"
    assert data["source"] == "forwarded"


def test_me_returns_dev_identity_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("DEV_USER", "devuser")
    monkeypatch.setenv("DEV_EMAIL", "dev@example.com")
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)

    response = client.get("/api/v1/me")

    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "devuser"
    assert data["email"] == "dev@example.com"
    assert data["preferred_username"] is None
    assert data["source"] == "dev"


def test_me_requires_identity(monkeypatch) -> None:
    monkeypatch.delenv("DEV_USER", raising=False)
    monkeypatch.delenv("DEV_EMAIL", raising=False)
    monkeypatch.setenv("DATABRICKS_HOST", "https://example")

    response = client.get("/api/v1/me")

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["message"] == "Missing user identity"
