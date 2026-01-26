"""Tests for status list endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_desc(items: list[dict], fields: tuple[str, ...]) -> None:
    expected = sorted(
        items,
        key=lambda item: tuple(item[field] for field in fields),
        reverse=True,
    )
    assert items == expected


def _assert_pagination(path: str, fields: tuple[str, ...]) -> None:
    response = client.get(path, params={"limit": 200})
    assert response.status_code == 200
    data = response.json()
    items = data["items"]

    assert data["limit"] == 200
    assert data["offset"] == 0
    assert data["total"] >= len(items)
    _assert_desc(items, fields)

    if len(items) < 2:
        pytest.skip("Not enough items to validate pagination")

    page_response = client.get(path, params={"limit": 1, "offset": 1})
    assert page_response.status_code == 200
    page_data = page_response.json()

    assert page_data["limit"] == 1
    assert page_data["offset"] == 1
    assert page_data["total"] == data["total"]
    assert page_data["items"] == items[1:2]


def test_platforms_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/platforms", ("created_at", "id"))


def test_status_results_pagination_and_ordering() -> None:
    _assert_pagination(
        "/api/v1/status-results",
        ("measured_at", "created_at", "id"),
    )


def test_status_checks_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/status-checks", ("created_at", "id"))


def test_status_messages_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/status-messages", ("created_at", "id"))


def test_status_results_filters() -> None:
    response = client.get("/api/v1/status-results")
    assert response.status_code == 200
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status results available to validate filters")

    platform_id = items[0]["platform_id"]
    check_id = items[0]["check_id"]

    platform_response = client.get(
        "/api/v1/status-results", params={"platform_id": platform_id}
    )
    assert platform_response.status_code == 200
    platform_items = platform_response.json().get("items", [])
    assert all(item["platform_id"] == platform_id for item in platform_items)

    check_response = client.get(
        "/api/v1/status-results", params={"check_id": check_id}
    )
    assert check_response.status_code == 200
    check_items = check_response.json().get("items", [])
    assert all(item["check_id"] == check_id for item in check_items)

    measured_values = sorted({item["measured_at"] for item in items})
    if len(measured_values) < 2:
        pytest.skip("Not enough unique timestamps to validate time range filters")

    start_at = measured_values[-1]
    start_response = client.get(
        "/api/v1/status-results", params={"start_at": start_at}
    )
    assert start_response.status_code == 200
    start_items = start_response.json().get("items", [])
    assert all(item["measured_at"] >= start_at for item in start_items)

    end_at = measured_values[0]
    end_response = client.get(
        "/api/v1/status-results", params={"end_at": end_at}
    )
    assert end_response.status_code == 200
    end_items = end_response.json().get("items", [])
    assert all(item["measured_at"] <= end_at for item in end_items)


def test_status_results_latest() -> None:
    response = client.get("/api/v1/status-results")
    assert response.status_code == 200
    items = response.json().get("items", [])

    if not items:
        pytest.skip("No status results available to validate latest endpoint")

    latest_response = client.get("/api/v1/status-results/latest")
    assert latest_response.status_code == 200
    latest_items = latest_response.json().get("items", [])

    assert len(latest_items) == len({item["check_id"] for item in latest_items})
    _assert_desc(latest_items, ("measured_at", "created_at", "id"))

    by_check: dict[str, list[dict]] = {}
    for item in items:
        by_check.setdefault(item["check_id"], []).append(item)

    check_id = None
    expected_latest: dict | None = None
    for candidate, entries in by_check.items():
        if len(entries) > 1:
            check_id = candidate
            expected_latest = max(
                entries,
                key=lambda item: (item["measured_at"], item["created_at"], item["id"]),
            )
            break

    if check_id is None or expected_latest is None:
        pytest.skip("No status check has multiple results to validate latest selection")

    filtered_latest = client.get(
        "/api/v1/status-results/latest", params={"check_id": check_id}
    )
    assert filtered_latest.status_code == 200
    filtered_items = filtered_latest.json().get("items", [])

    assert len(filtered_items) == 1
    assert filtered_items[0]["id"] == expected_latest["id"]
