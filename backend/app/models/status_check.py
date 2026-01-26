"""Status check API models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StatusCheckBase(BaseModel):
    platform_id: str = Field(min_length=1, max_length=200)
    name: str = Field(min_length=1, max_length=200)
    check_type: str = Field(min_length=1, max_length=100)
    owner_group: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    sla_minutes: int = Field(gt=0)
    warn_after_minutes: int = Field(gt=0)
    crit_after_minutes: int = Field(gt=0)
    state: str = Field(min_length=1, max_length=50)

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def _validate_thresholds(self) -> "StatusCheckBase":
        if self.warn_after_minutes >= self.crit_after_minutes:
            raise ValueError("warn_after_minutes must be less than crit_after_minutes")
        return self


class StatusCheckCreate(StatusCheckBase):
    pass


class StatusCheckUpdate(StatusCheckBase):
    pass


class StatusCheckRead(StatusCheckBase):
    id: str
    version: int
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    is_deleted: bool = False
    deleted_at: Optional[str] = None
    deleted_by: Optional[str] = None


class StatusCheckListResponse(BaseModel):
    items: list[StatusCheckRead]
    total: int
    limit: int
    offset: int
