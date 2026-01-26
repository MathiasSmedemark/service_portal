"""Local fixture repository for early development."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from app.db.interfaces import PlatformRepository, StatusRepository, WorkItemRepository
from app.db.models import Platform, StatusCheck, StatusMessage, StatusResult, WorkItem

_DEFAULT_PLATFORMS = (
    Platform(
        id="platform-001",
        name="Databricks",
        owner="Platform Ops",
        state="operational",
        created_at="2024-06-01T08:00:00Z",
        updated_at="2024-07-12T09:15:00Z",
    ),
    Platform(
        id="platform-002",
        name="Power BI",
        owner="BI Enablement",
        state="monitoring",
        created_at="2024-05-20T08:00:00Z",
        updated_at="2024-07-12T09:10:00Z",
    ),
    Platform(
        id="platform-003",
        name="Service Portal",
        owner="Platform Ops",
        state="operational",
        created_at="2024-07-01T08:00:00Z",
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

_DEFAULT_STATUS_RESULTS = (
    StatusResult(
        id="result-002",
        check_id="status-002",
        platform_id="platform-002",
        state="yellow",
        measured_at="2024-07-12T09:08:00Z",
        created_at="2024-07-12T09:10:30Z",
        observed_value="freshness=22m",
        message="Sync delayed during maintenance",
        ingestion_run_id="run-001",
    ),
    StatusResult(
        id="result-001",
        check_id="status-001",
        platform_id="platform-001",
        state="green",
        measured_at="2024-07-12T09:14:00Z",
        created_at="2024-07-12T09:15:30Z",
        observed_value="freshness=6m",
        message="All clusters responding",
        ingestion_run_id="run-001",
    ),
    StatusResult(
        id="result-003",
        check_id="status-003",
        platform_id="platform-003",
        state="green",
        measured_at="2024-07-12T09:12:00Z",
        created_at="2024-07-12T09:09:30Z",
        observed_value="freshness=3m",
        message="Latency within SLA",
        ingestion_run_id="run-001",
    ),
)

_DEFAULT_STATUS_MESSAGES = (
    StatusMessage(
        id="message-001",
        platform_id=None,
        severity="info",
        title="Scheduled maintenance",
        body_md="Routine maintenance window.",
        state="published",
        created_at="2024-07-10T08:00:00Z",
        start_at="2024-07-12T23:00:00Z",
        end_at="2024-07-13T01:00:00Z",
    ),
    StatusMessage(
        id="message-002",
        platform_id="platform-002",
        severity="warning",
        title="Power BI refresh delays",
        body_md="Datasets may refresh late.",
        state="published",
        created_at="2024-07-12T07:30:00Z",
        start_at="2024-07-12T07:00:00Z",
        end_at=None,
    ),
    StatusMessage(
        id="message-003",
        platform_id="platform-001",
        severity="critical",
        title="Warehouse incident",
        body_md="Investigating intermittent errors.",
        state="draft",
        created_at="2024-07-11T14:00:00Z",
        start_at=None,
        end_at=None,
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
        status_results: Iterable[StatusResult] | None = None,
        status_messages: Iterable[StatusMessage] | None = None,
        work_items: Iterable[WorkItem] | None = None,
    ) -> None:
        self._platforms = list(platforms or _DEFAULT_PLATFORMS)
        self._status_checks = list(status_checks or _DEFAULT_STATUS_CHECKS)
        self._status_results = list(status_results or _DEFAULT_STATUS_RESULTS)
        self._status_messages = list(status_messages or _DEFAULT_STATUS_MESSAGES)
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

    def list_status_results(self) -> Sequence[StatusResult]:
        return list(self._status_results)

    def list_status_messages(self) -> Sequence[StatusMessage]:
        return list(self._status_messages)

    def list_work_items(self, state: Optional[str] = None) -> Sequence[WorkItem]:
        if not state:
            return list(self._work_items)
        return [item for item in self._work_items if item.state == state]
