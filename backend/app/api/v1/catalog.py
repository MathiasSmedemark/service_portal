"""Stub read-only endpoints backed by local fixtures."""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.db.deps import get_repository

router = APIRouter(prefix="/api/v1")


def _paginate(items: list, limit: int, offset: int) -> tuple[list, int, int, int]:
    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit must be between 1 and 200",
        )
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="offset must be >= 0",
        )
    total = len(items)
    return items[offset : offset + limit], total, limit, offset


def _order_by_created_desc(items: list) -> list:
    return sorted(items, key=lambda item: (item.created_at, item.id), reverse=True)


@router.get("/status-results")
def list_status_results(limit: int = 25, offset: int = 0) -> dict:
    repo = get_repository()
    results = _order_by_created_desc(list(repo.list_status_results()))
    page, total, limit, offset = _paginate(results, limit, offset)
    return {
        "items": [asdict(result) for result in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/status-messages")
def list_status_messages(limit: int = 25, offset: int = 0) -> dict:
    repo = get_repository()
    messages = _order_by_created_desc(list(repo.list_status_messages()))
    page, total, limit, offset = _paginate(messages, limit, offset)
    return {
        "items": [asdict(message) for message in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/work-items")
def list_work_items(state: Optional[str] = None, limit: int = 25, offset: int = 0) -> dict:
    repo = get_repository()
    items = [asdict(item) for item in repo.list_work_items(state=state)]
    page, total, limit, offset = _paginate(items, limit, offset)
    return {"items": page, "total": total, "limit": limit, "offset": offset}
