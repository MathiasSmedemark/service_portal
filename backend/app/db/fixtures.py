"""Local fixture repository for early development."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from app.db.interfaces import PlatformRepository, StatusRepository, WorkItemRepository
from app.db.mock_data import (
    DEFAULT_PLATFORMS,
    DEFAULT_STATUS_CHECKS,
    DEFAULT_STATUS_MESSAGES,
    DEFAULT_STATUS_RESULTS,
    DEFAULT_WORK_ITEMS,
)
from app.db.models import Platform, StatusCheck, StatusMessage, StatusResult, WorkItem


class LocalFixtureRepository(PlatformRepository, StatusRepository, WorkItemRepository):
    def __init__(
        self,
        platforms: Iterable[Platform] | None = None,
        status_checks: Iterable[StatusCheck] | None = None,
        status_results: Iterable[StatusResult] | None = None,
        status_messages: Iterable[StatusMessage] | None = None,
        work_items: Iterable[WorkItem] | None = None,
    ) -> None:
        self._platforms = list(platforms or DEFAULT_PLATFORMS)
        self._status_checks = list(status_checks or DEFAULT_STATUS_CHECKS)
        self._status_results = list(status_results or DEFAULT_STATUS_RESULTS)
        self._status_messages = list(status_messages or DEFAULT_STATUS_MESSAGES)
        self._work_items = list(work_items or DEFAULT_WORK_ITEMS)

    def list_platforms(self) -> Sequence[Platform]:
        return list(self._platforms)

    def get_platform(self, platform_id: str) -> Optional[Platform]:
        for platform in self._platforms:
            if platform.id == platform_id:
                return platform
        return None

    def create_platform(self, platform: Platform) -> Platform:
        self._platforms.append(platform)
        return platform

    def list_status_checks(self, platform_id: Optional[str] = None) -> Sequence[StatusCheck]:
        if not platform_id:
            return list(self._status_checks)
        return [item for item in self._status_checks if item.platform_id == platform_id]

    def list_status_results(self) -> Sequence[StatusResult]:
        return list(self._status_results)

    def list_status_messages(self) -> Sequence[StatusMessage]:
        return list(self._status_messages)

    def list_work_items(self, state: Optional[str] = None) -> Sequence[WorkItem]:
        if not state:
            return list(self._work_items)
        return [item for item in self._work_items if item.state == state]
