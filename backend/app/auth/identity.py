"""Identity extraction for forwarded headers and local dev overrides."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

FORWARDED_USER_HEADER = "x-forwarded-user"
FORWARDED_EMAIL_HEADER = "x-forwarded-email"
FORWARDED_PREFERRED_USERNAME_HEADER = "x-forwarded-preferred-username"

DEV_USER_ENV = "DEV_USER"
DEV_EMAIL_ENV = "DEV_EMAIL"
DATABRICKS_HOST_ENV = "DATABRICKS_HOST"
DATABRICKS_APP_PORT_ENV = "DATABRICKS_APP_PORT"


@dataclass(frozen=True)
class Identity:
    user: str
    email: Optional[str]
    preferred_username: Optional[str]
    source: str


def _normalize_headers(headers: Mapping[str, str]) -> dict:
    return {key.lower(): value for key, value in headers.items()}


def _dev_override_allowed(env: Mapping[str, str]) -> bool:
    return not (env.get(DATABRICKS_HOST_ENV) or env.get(DATABRICKS_APP_PORT_ENV))


def extract_identity(headers: Mapping[str, str], env: Mapping[str, str]) -> Optional[Identity]:
    normalized = _normalize_headers(headers)

    forwarded_user = normalized.get(FORWARDED_USER_HEADER)
    forwarded_email = normalized.get(FORWARDED_EMAIL_HEADER)
    preferred_username = normalized.get(FORWARDED_PREFERRED_USERNAME_HEADER)

    if forwarded_user or forwarded_email:
        user = forwarded_user or forwarded_email
        return Identity(
            user=user,
            email=forwarded_email,
            preferred_username=preferred_username,
            source="forwarded",
        )

    if _dev_override_allowed(env):
        dev_user = env.get(DEV_USER_ENV)
        dev_email = env.get(DEV_EMAIL_ENV)
        if dev_user or dev_email:
            user = dev_user or dev_email
            return Identity(
                user=user,
                email=dev_email,
                preferred_username=None,
                source="dev",
            )

    return None
