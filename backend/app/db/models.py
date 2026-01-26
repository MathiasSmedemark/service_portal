"""Data models for repository fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Platform:
    id: str
    name: str
    owner: str
    state: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


@dataclass(frozen=True)
class StatusCheck:
    id: str
    platform_id: str
    name: str
    state: str
    checked_at: str
    message: str
    sla_minutes: int
    freshness_minutes: int


@dataclass(frozen=True)
class StatusResult:
    id: str
    check_id: str
    platform_id: str
    state: str
    measured_at: str
    created_at: str
    observed_value: Optional[str] = None
    message: Optional[str] = None
    ingestion_run_id: Optional[str] = None


@dataclass(frozen=True)
class StatusMessage:
    id: str
    platform_id: Optional[str]
    severity: str
    title: str
    body_md: str
    state: str
    created_at: str
    start_at: Optional[str] = None
    end_at: Optional[str] = None


@dataclass(frozen=True)
class WorkItem:
    id: str
    platform_id: Optional[str]
    title: str
    state: str
    priority: str
    created_at: str
    requester: str
