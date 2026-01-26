"""Platform API models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PlatformBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    owner: str = Field(min_length=1, max_length=200)
    state: str = Field(min_length=1, max_length=50)

    model_config = ConfigDict(str_strip_whitespace=True)


class PlatformCreate(PlatformBase):
    pass


class PlatformRead(PlatformBase):
    id: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class PlatformListResponse(BaseModel):
    items: list[PlatformRead]
    total: int
    limit: int
    offset: int
