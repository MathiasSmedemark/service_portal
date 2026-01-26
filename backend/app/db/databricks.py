"""Databricks-backed repository stubs (read-only)."""

from __future__ import annotations

from typing import Optional, Sequence

from app.db.interfaces import PlatformRepository, StatusRepository, WorkItemRepository
from app.db.models import Platform, StatusCheck, StatusMessage, StatusResult, WorkItem


class DatabricksRepository(PlatformRepository, StatusRepository, WorkItemRepository):
    def list_platforms(self) -> Sequence[Platform]:
        raise NotImplementedError("Databricks adapter not implemented yet")

    def get_platform(self, platform_id: str) -> Optional[Platform]:
        raise NotImplementedError("Databricks adapter not implemented yet")

    def list_status_checks(self, platform_id: Optional[str] = None) -> Sequence[StatusCheck]:
        raise NotImplementedError("Databricks adapter not implemented yet")

    def list_status_results(self) -> Sequence[StatusResult]:
        raise NotImplementedError("Databricks adapter not implemented yet")

    def list_status_messages(self) -> Sequence[StatusMessage]:
        raise NotImplementedError("Databricks adapter not implemented yet")

    def list_work_items(self, state: Optional[str] = None) -> Sequence[WorkItem]:
        raise NotImplementedError("Databricks adapter not implemented yet")
