"""Tests for status check configuration endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _admin_headers() -> dict[str, str]:
    return {"X-Forwarded-User": "devuser"}


def _sample_payload(platform_id: str) -> dict:
    return {
        "platform_id": platform_id,
        "name": "Freshness check",
        "check_type": "freshness",
        "owner_group": "Platform Ops",
        "description": "Checks that platform data stays fresh.",
        "sla_minutes": 15,
        "warn_after_minutes": 30,
        "crit_after_minutes": 60,
        "state": "enabled",
    }


def test_list_status_checks_returns_items() -> None:
    response = client.get("/api/v1/status-checks")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("items"), list)
    assert payload["total"] >= len(payload["items"])


def test_filter_status_checks_by_platform() -> None:
    response = client.get("/api/v1/status-checks")
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status checks available to validate filtering")

    platform_id = items[0]["platform_id"]
    filtered_response = client.get(
        "/api/v1/status-checks", params={"platform_id": platform_id}
    )
    assert filtered_response.status_code == 200
    filtered_items = filtered_response.json().get("items", [])
    assert all(item["platform_id"] == platform_id for item in filtered_items)


def test_get_status_check_by_id() -> None:
    response = client.get("/api/v1/status-checks")
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status checks available to validate detail endpoint")

    check_id = items[0]["id"]
    detail_response = client.get(f"/api/v1/status-checks/{check_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == check_id


def test_create_and_update_status_check() -> None:
    response = client.get("/api/v1/status-checks")
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status checks available to validate create/update")

    platform_id = items[0]["platform_id"]
    payload = _sample_payload(platform_id)
    create_response = client.post(
        "/api/v1/status-checks",
        json=payload,
        headers=_admin_headers(),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["platform_id"] == platform_id

    update_payload = {
        **payload,
        "name": "Freshness check updated",
        "warn_after_minutes": 35,
        "crit_after_minutes": 70,
    }
    update_response = client.put(
        f"/api/v1/status-checks/{created['id']}",
        json=update_payload,
        headers=_admin_headers(),
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Freshness check updated"
    assert updated["version"] == created["version"] + 1


def test_create_status_check_validates_thresholds() -> None:
    response = client.get("/api/v1/status-checks")
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status checks available to validate thresholds")

    platform_id = items[0]["platform_id"]
    payload = _sample_payload(platform_id)
    payload["warn_after_minutes"] = payload["crit_after_minutes"]

    invalid_response = client.post(
        "/api/v1/status-checks",
        json=payload,
        headers=_admin_headers(),
    )

    assert invalid_response.status_code == 422
