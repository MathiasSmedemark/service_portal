"""Local fixture repository for early development."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from app.db.interfaces import PlatformRepository, StatusRepository, WorkItemRepository
from app.db.models import Platform, StatusCheck, WorkItem

_DEFAULT_PLATFORMS = (
    Platform(
        id="platform-001",
        name="Databricks",
        owner="Platform Ops",
        state="operational",
        updated_at="2024-07-12T09:15:00Z",
    ),
    Platform(
        id="platform-002",
        name="Power BI",
        owner="BI Enablement",
        state="monitoring",
        updated_at="2024-07-12T09:10:00Z",
    ),
    Platform(
        id="platform-003",
        name="Service Portal",
        owner="Platform Ops",
        state="operational",
        updated_at="2024-07-12T09:05:00Z",
    ),
)

_DEFAULT_STATUS_CHECKS = (
    StatusCheck(
        id="status-001",
        platform_id="platform-001",
        name="SQL Warehouse Refresh",
        state="ok",
        checked_at="2024-07-12T09:14:00Z",
        message="All clusters responding",
        sla_minutes=15,
        freshness_minutes=6,
    ),
    StatusCheck(
        id="status-002",
        platform_id="platform-002",
        name="Dataset Sync",
        state="warning",
        checked_at="2024-07-12T09:08:00Z",
        message="Sync delayed during maintenance",
        sla_minutes=30,
        freshness_minutes=22,
    ),
    StatusCheck(
        id="status-003",
        platform_id="platform-003",
        name="Portal API",
        state="ok",
        checked_at="2024-07-12T09:12:00Z",
        message="Latency within SLA",
        sla_minutes=10,
        freshness_minutes=3,
    ),
)

_DEFAULT_WORK_ITEMS = (
    WorkItem(
        id="work-001",
        platform_id="platform-001",
        title="Access request: finance workspace",
        state="open",
        priority="medium",
        created_at="2024-07-12T08:30:00Z",
        requester="alex@example.com",
    ),
    WorkItem(
        id="work-002",
        platform_id="platform-002",
        title="Incident: refresh lag",
        state="triage",
        priority="high",
        created_at="2024-07-12T07:55:00Z",
        requester="bi-ops@example.com",
    ),
    WorkItem(
        id="work-003",
        platform_id=None,
        title="Doc update: onboarding checklist",
        state="open",
        priority="low",
        created_at="2024-07-11T16:20:00Z",
        requester="docs@example.com",
    ),
)


class LocalFixtureRepository(PlatformRepository, StatusRepository, WorkItemRepository):
    def __init__(
        self,
        platforms: Iterable[Platform] | None = None,
        status_checks: Iterable[StatusCheck] | None = None,
        work_items: Iterable[WorkItem] | None = None,
    ) -> None:
        self._platforms = list(platforms or _DEFAULT_PLATFORMS)
        self._status_checks = list(status_checks or _DEFAULT_STATUS_CHECKS)
        self._work_items = list(work_items or _DEFAULT_WORK_ITEMS)

    def list_platforms(self) -> Sequence[Platform]:
        return list(self._platforms)

    def get_platform(self, platform_id: str) -> Optional[Platform]:
        for platform in self._platforms:
            if platform.id == platform_id:
                return platform
        return None

    def list_status_checks(self, platform_id: Optional[str] = None) -> Sequence[StatusCheck]:
        if not platform_id:
            return list(self._status_checks)
        return [item for item in self._status_checks if item.platform_id == platform_id]

    def list_work_items(self, state: Optional[str] = None) -> Sequence[WorkItem]:
        if not state:
            return list(self._work_items)
        return [item for item in self._work_items if item.state == state]
