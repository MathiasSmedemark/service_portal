"""Tests for status list endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _assert_desc(items: list[dict]) -> None:
    expected = sorted(
        items,
        key=lambda item: (item["created_at"], item["id"]),
        reverse=True,
    )
    assert items == expected


def _assert_pagination(path: str) -> None:
    response = client.get(path, params={"limit": 200})
    assert response.status_code == 200
    data = response.json()
    items = data["items"]

    assert data["limit"] == 200
    assert data["offset"] == 0
    assert data["total"] >= len(items)
    _assert_desc(items)

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
    _assert_pagination("/api/v1/platforms")


def test_status_results_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/status-results")


def test_status_checks_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/status-checks")


def test_status_messages_pagination_and_ordering() -> None:
    _assert_pagination("/api/v1/status-messages")
