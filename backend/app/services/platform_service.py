"""Platform service layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.auth.identity import Identity
from app.core.exceptions import NotFoundError
from app.db.deps import get_repository
from app.db.interfaces import PlatformRepository
from app.db.models import Platform
from app.models.platform import PlatformCreate


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class PlatformService:
    def __init__(self, repository: PlatformRepository) -> None:
        self._repository = repository

    def list_platforms(self) -> list[Platform]:
        return list(self._repository.list_platforms())

    def get_platform(self, platform_id: str) -> Platform:
        platform = self._repository.get_platform(platform_id)
        if platform is None:
            raise NotFoundError("Platform not found")
        return platform

    def create_platform(self, payload: PlatformCreate, identity: Identity) -> Platform:
        timestamp = _utc_now()
        platform = Platform(
            id=str(uuid.uuid4()),
            name=payload.name,
            owner=payload.owner,
            state=payload.state,
            created_at=timestamp,
            created_by=identity.user,
            updated_at=timestamp,
            updated_by=identity.user,
        )
        self._repository.create_platform(platform)
        return platform


def get_platform_service() -> PlatformService:
    return PlatformService(get_repository())
