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
    updated_at: str


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
class WorkItem:
    id: str
    platform_id: Optional[str]
    title: str
    state: str
    priority: str
    created_at: str
    requester: str
