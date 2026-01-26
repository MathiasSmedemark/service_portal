"""Status check configuration service layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.auth.identity import Identity
from app.core.exceptions import NotFoundError
from app.db.deps import get_repository
from app.db.interfaces import StatusRepository
from app.db.models import StatusCheck
from app.models.status_check import StatusCheckCreate, StatusCheckUpdate


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class StatusCheckService:
    def __init__(self, repository: StatusRepository) -> None:
        self._repository = repository

    def list_status_checks(self, platform_id: Optional[str] = None) -> list[StatusCheck]:
        return list(self._repository.list_status_checks(platform_id=platform_id))

    def get_status_check(self, check_id: str) -> StatusCheck:
        check = self._repository.get_status_check(check_id)
        if check is None:
            raise NotFoundError("Status check not found")
        return check

    def create_status_check(
        self, payload: StatusCheckCreate, identity: Identity
    ) -> StatusCheck:
        timestamp = _utc_now()
        check = StatusCheck(
            id=str(uuid.uuid4()),
            platform_id=payload.platform_id,
            name=payload.name,
            check_type=payload.check_type,
            owner_group=payload.owner_group,
            description=payload.description,
            sla_minutes=payload.sla_minutes,
            warn_after_minutes=payload.warn_after_minutes,
            crit_after_minutes=payload.crit_after_minutes,
            state=payload.state,
            version=1,
            created_at=timestamp,
            created_by=identity.user,
            updated_at=timestamp,
            updated_by=identity.user,
            is_deleted=False,
            deleted_at=None,
            deleted_by=None,
        )
        self._repository.create_status_check(check)
        return check

    def update_status_check(
        self, check_id: str, payload: StatusCheckUpdate, identity: Identity
    ) -> StatusCheck:
        existing = self.get_status_check(check_id)
        timestamp = _utc_now()
        updated = StatusCheck(
            id=existing.id,
            platform_id=payload.platform_id,
            name=payload.name,
            check_type=payload.check_type,
            owner_group=payload.owner_group,
            description=payload.description,
            sla_minutes=payload.sla_minutes,
            warn_after_minutes=payload.warn_after_minutes,
            crit_after_minutes=payload.crit_after_minutes,
            state=payload.state,
            version=existing.version + 1,
            created_at=existing.created_at,
            created_by=existing.created_by,
            updated_at=timestamp,
            updated_by=identity.user,
            is_deleted=existing.is_deleted,
            deleted_at=existing.deleted_at,
            deleted_by=existing.deleted_by,
        )
        self._repository.update_status_check(updated)
        return updated


def get_status_check_service() -> StatusCheckService:
    return StatusCheckService(get_repository())
