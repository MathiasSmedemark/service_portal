"""Platform endpoints."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_current_user
from app.auth.identity import Identity
from app.auth.permissions import PermissionContext, require_role
from app.core.exceptions import ForbiddenError
from app.models.platform import PlatformCreate, PlatformListResponse, PlatformRead
from app.services.platform_service import PlatformService, get_platform_service
from app.services.rbac_service import ROLE_ADMIN

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


@router.get("/platforms", response_model=PlatformListResponse)
def list_platforms(
    limit: int = 25,
    offset: int = 0,
    service: PlatformService = Depends(get_platform_service),
) -> dict:
    platforms = _order_by_created_desc(list(service.list_platforms()))
    page, total, limit, offset = _paginate(platforms, limit, offset)
    return {
        "items": [asdict(platform) for platform in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/platforms/{platform_id}", response_model=PlatformRead)
def get_platform(
    platform_id: str, service: PlatformService = Depends(get_platform_service)
) -> dict:
    platform = service.get_platform(platform_id)
    return asdict(platform)


@router.post(
    "/platforms",
    status_code=status.HTTP_201_CREATED,
    response_model=PlatformRead,
)
def create_platform(
    payload: PlatformCreate,
    identity: Identity = Depends(get_current_user),
    permissions: PermissionContext = Depends(require_role(ROLE_ADMIN)),
    service: PlatformService = Depends(get_platform_service),
) -> dict:
    if not permissions.granted:
        raise ForbiddenError("Admin role required")
    platform = service.create_platform(payload, identity)
    return asdict(platform)
