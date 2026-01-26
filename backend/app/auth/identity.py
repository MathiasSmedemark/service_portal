"""Identity extraction for forwarded headers and local dev overrides."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from app.core.config import Settings

FORWARDED_USER_HEADER = "x-forwarded-user"
FORWARDED_EMAIL_HEADER = "x-forwarded-email"
FORWARDED_PREFERRED_USERNAME_HEADER = "x-forwarded-preferred-username"


@dataclass(frozen=True)
class Identity:
    user: str
    email: Optional[str]
    preferred_username: Optional[str]
    source: str


def _normalize_headers(headers: Mapping[str, str]) -> dict:
    return {key.lower(): value for key, value in headers.items()}


def extract_identity(headers: Mapping[str, str], settings: Settings) -> Optional[Identity]:
    normalized = _normalize_headers(headers)

    forwarded_user = normalized.get(FORWARDED_USER_HEADER)
    forwarded_email = normalized.get(FORWARDED_EMAIL_HEADER)
    preferred_username = normalized.get(FORWARDED_PREFERRED_USERNAME_HEADER)

    if forwarded_user is not None or forwarded_email is not None:
        user = forwarded_user if forwarded_user is not None else forwarded_email
        assert user is not None
        return Identity(
            user=user,
            email=forwarded_email,
            preferred_username=preferred_username,
            source="forwarded",
        )

    if settings.dev_override_enabled:
        dev_user = settings.dev_user
        dev_email = settings.dev_email
        if dev_user is not None or dev_email is not None:
            user = dev_user if dev_user is not None else dev_email
            assert user is not None
            return Identity(
                user=user,
                email=dev_email,
                preferred_username=None,
                source="dev",
            )

    return None
