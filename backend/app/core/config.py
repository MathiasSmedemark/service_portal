"""Application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    databricks_host: str | None = None
    databricks_app_port: int = 8000
    dev_user: str | None = None
    dev_email: str | None = None

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="",
        extra="ignore",
    )

    @property
    def dev_override_enabled(self) -> bool:
        return not self.databricks_host


@lru_cache
def get_settings() -> Settings:
    return Settings()
