"""Status check configuration endpoints."""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_current_user
from app.auth.identity import Identity
from app.auth.permissions import PermissionContext, require_role
from app.core.exceptions import ForbiddenError
from app.models.status_check import (
    StatusCheckCreate,
    StatusCheckListResponse,
    StatusCheckRead,
    StatusCheckUpdate,
)
from app.services.rbac_service import ROLE_ADMIN
from app.services.status_check_service import (
    StatusCheckService,
    get_status_check_service,
)

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


@router.get("/status-checks", response_model=StatusCheckListResponse)
def list_status_checks(
    platform_id: Optional[str] = None,
    limit: int = 25,
    offset: int = 0,
    service: StatusCheckService = Depends(get_status_check_service),
) -> dict:
    checks = _order_by_created_desc(
        list(service.list_status_checks(platform_id=platform_id))
    )
    page, total, limit, offset = _paginate(checks, limit, offset)
    return {
        "items": [asdict(check) for check in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/status-checks/{check_id}", response_model=StatusCheckRead)
def get_status_check(
    check_id: str, service: StatusCheckService = Depends(get_status_check_service)
) -> dict:
    check = service.get_status_check(check_id)
    return asdict(check)


@router.post(
    "/status-checks",
    status_code=status.HTTP_201_CREATED,
    response_model=StatusCheckRead,
)
def create_status_check(
    payload: StatusCheckCreate,
    identity: Identity = Depends(get_current_user),
    permissions: PermissionContext = Depends(require_role(ROLE_ADMIN)),
    service: StatusCheckService = Depends(get_status_check_service),
) -> dict:
    if not permissions.granted:
        raise ForbiddenError("Admin role required")
    check = service.create_status_check(payload, identity)
    return asdict(check)


@router.put("/status-checks/{check_id}", response_model=StatusCheckRead)
def update_status_check(
    check_id: str,
    payload: StatusCheckUpdate,
    identity: Identity = Depends(get_current_user),
    permissions: PermissionContext = Depends(require_role(ROLE_ADMIN)),
    service: StatusCheckService = Depends(get_status_check_service),
) -> dict:
    if not permissions.granted:
        raise ForbiddenError("Admin role required")
    check = service.update_status_check(check_id, payload, identity)
    return asdict(check)
