"""Permission dependency stubs for RBAC enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from fastapi import Depends

from app.auth.deps import get_optional_user
from app.auth.identity import Identity
from app.services.rbac_service import RBACService, get_rbac_service


@dataclass(frozen=True)
class PermissionContext:
    identity: Optional[Identity]
    roles: frozenset[str]
    required_roles: tuple[str, ...]
    platform_id: Optional[str]
    granted: bool


def has_any_role(roles: Iterable[str], required_roles: Iterable[str]) -> bool:
    required = set(required_roles)
    if not required:
        return True
    role_set = set(roles)
    return any(role in role_set for role in required)


def _normalize_roles(roles: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(role for role in roles if role))


def require_roles(
    *required_roles: str,
    platform_id: Optional[str] = None,
) -> Callable[..., PermissionContext]:
    normalized = _normalize_roles(required_roles)

    def dependency(
        identity: Optional[Identity] = Depends(get_optional_user),
        rbac: RBACService = Depends(get_rbac_service),
    ) -> PermissionContext:
        roles = rbac.get_roles(identity, platform_id=platform_id)
        granted = has_any_role(roles, normalized)
        return PermissionContext(
            identity=identity,
            roles=frozenset(roles),
            required_roles=normalized,
            platform_id=platform_id,
            granted=granted,
        )

    return dependency


def require_role(role: str, platform_id: Optional[str] = None) -> Callable[..., PermissionContext]:
    return require_roles(role, platform_id=platform_id)
