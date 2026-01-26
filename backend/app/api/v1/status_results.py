"""Status result query endpoints."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.db.deps import get_repository
from app.db.models import StatusResult

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


def _normalize_timestamp(value: str) -> str:
    if value.endswith("Z"):
        return f"{value[:-1]}+00:00"
    return value


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(_normalize_timestamp(value))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_query_timestamp(value: str, label: str) -> datetime:
    try:
        return _parse_timestamp(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label} must be ISO-8601",
        ) from exc


def _parse_result_timestamp(value: str) -> datetime:
    try:
        return _parse_timestamp(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid timestamp in status results",
        ) from exc


def _sort_key(result: StatusResult) -> tuple[datetime, datetime, str]:
    return (
        _parse_result_timestamp(result.measured_at),
        _parse_result_timestamp(result.created_at),
        result.id,
    )


def _order_by_measured_desc(items: list[StatusResult]) -> list[StatusResult]:
    return sorted(items, key=_sort_key, reverse=True)


def _validate_time_range(
    start_at: Optional[str], end_at: Optional[str]
) -> tuple[Optional[datetime], Optional[datetime]]:
    start_dt = _parse_query_timestamp(start_at, "start_at") if start_at else None
    end_dt = _parse_query_timestamp(end_at, "end_at") if end_at else None
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_at must be <= end_at",
        )
    return start_dt, end_dt


def _filter_results(
    results: list[StatusResult],
    platform_id: Optional[str],
    check_id: Optional[str],
    start_at: Optional[str],
    end_at: Optional[str],
) -> list[StatusResult]:
    start_dt, end_dt = _validate_time_range(start_at, end_at)
    filtered: list[StatusResult] = []
    for result in results:
        if platform_id and result.platform_id != platform_id:
            continue
        if check_id and result.check_id != check_id:
            continue
        measured_dt = _parse_result_timestamp(result.measured_at)
        if start_dt and measured_dt < start_dt:
            continue
        if end_dt and measured_dt > end_dt:
            continue
        filtered.append(result)
    return filtered


@router.get("/status-results")
def list_status_results(
    platform_id: Optional[str] = None,
    check_id: Optional[str] = None,
    start_at: Optional[str] = None,
    end_at: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    repo = get_repository()
    results = list(repo.list_status_results())
    filtered = _filter_results(results, platform_id, check_id, start_at, end_at)
    ordered = _order_by_measured_desc(filtered)
    page, total, limit, offset = _paginate(ordered, limit, offset)
    return {
        "items": [asdict(result) for result in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/status-results/latest")
def list_latest_status_results(
    platform_id: Optional[str] = None,
    check_id: Optional[str] = None,
    start_at: Optional[str] = None,
    end_at: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    repo = get_repository()
    results = list(repo.list_status_results())
    filtered = _filter_results(results, platform_id, check_id, start_at, end_at)

    latest_by_check: dict[
        str,
        tuple[tuple[datetime, datetime, str], StatusResult],
    ] = {}
    for result in filtered:
        sort_key = _sort_key(result)
        existing = latest_by_check.get(result.check_id)
        if existing is None or sort_key > existing[0]:
            latest_by_check[result.check_id] = (sort_key, result)

    latest = [entry[1] for entry in latest_by_check.values()]
    ordered = _order_by_measured_desc(latest)
    page, total, limit, offset = _paginate(ordered, limit, offset)
    return {
        "items": [asdict(result) for result in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
