"""Repository interfaces for platforms, status checks, and work items."""

from __future__ import annotations

from typing import Optional, Protocol, Sequence

from app.db.models import Platform, StatusCheck, StatusMessage, StatusResult, WorkItem


class PlatformRepository(Protocol):
    def list_platforms(self) -> Sequence[Platform]:
        raise NotImplementedError

    def get_platform(self, platform_id: str) -> Optional[Platform]:
        raise NotImplementedError

    def create_platform(self, platform: Platform) -> Platform:
        raise NotImplementedError


class StatusRepository(Protocol):
    def list_status_checks(self, platform_id: Optional[str] = None) -> Sequence[StatusCheck]:
        raise NotImplementedError

    def get_status_check(self, check_id: str) -> Optional[StatusCheck]:
        raise NotImplementedError

    def create_status_check(self, status_check: StatusCheck) -> StatusCheck:
        raise NotImplementedError

    def update_status_check(self, status_check: StatusCheck) -> StatusCheck:
        raise NotImplementedError

    def list_status_results(self) -> Sequence[StatusResult]:
        raise NotImplementedError

    def list_status_messages(self) -> Sequence[StatusMessage]:
        raise NotImplementedError


class WorkItemRepository(Protocol):
    def list_work_items(self, state: Optional[str] = None) -> Sequence[WorkItem]:
        raise NotImplementedError
