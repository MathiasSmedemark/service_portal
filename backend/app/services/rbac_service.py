"""RBAC service interfaces and local fixture implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

from app.auth.identity import Identity

ROLE_VIEWER = "Viewer"
ROLE_CONTRIBUTOR = "Contributor"
ROLE_INCIDENT_TRIAGER = "IncidentTriager"
ROLE_SERVICE_OWNER = "ServiceOwner"
ROLE_ADMIN = "Admin"


@dataclass(frozen=True)
class RoleBinding:
    id: str
    principal_type: str
    principal_id: str
    role: str
    platform_id: Optional[str]
    state: str
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str


class RBACService(Protocol):
    def get_roles(
        self,
        identity: Optional[Identity],
        platform_id: Optional[str] = None,
    ) -> set[str]:
        raise NotImplementedError

    def has_role(
        self,
        identity: Optional[Identity],
        role: str,
        platform_id: Optional[str] = None,
    ) -> bool:
        raise NotImplementedError


class LocalRBACService(RBACService):
    def __init__(self, bindings: Iterable[RoleBinding] | None = None) -> None:
        self._bindings = list(bindings or _DEFAULT_ROLE_BINDINGS)

    def get_roles(
        self,
        identity: Optional[Identity],
        platform_id: Optional[str] = None,
    ) -> set[str]:
        if identity is None:
            return set()

        principals = _identity_principals(identity)
        roles: set[str] = set()

        for binding in self._bindings:
            if binding.state != "active":
                continue
            if binding.principal_type != "user":
                continue
            if binding.principal_id not in principals:
                continue
            if platform_id is not None and binding.platform_id not in (None, platform_id):
                continue
            roles.add(binding.role)

        return roles

    def has_role(
        self,
        identity: Optional[Identity],
        role: str,
        platform_id: Optional[str] = None,
    ) -> bool:
        return role in self.get_roles(identity, platform_id=platform_id)


def _identity_principals(identity: Identity) -> set[str]:
    principals = {identity.user}
    if identity.email:
        principals.add(identity.email)
    if identity.preferred_username:
        principals.add(identity.preferred_username)
    return principals


_DEFAULT_ROLE_BINDINGS = (
    RoleBinding(
        id="rbac-001",
        principal_type="user",
        principal_id="devuser",
        role=ROLE_ADMIN,
        platform_id=None,
        state="active",
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    ),
    RoleBinding(
        id="rbac-002",
        principal_type="user",
        principal_id="viewer@example.com",
        role=ROLE_VIEWER,
        platform_id=None,
        state="active",
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    ),
    RoleBinding(
        id="rbac-003",
        principal_type="user",
        principal_id="contributor@example.com",
        role=ROLE_CONTRIBUTOR,
        platform_id="platform-001",
        state="active",
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    ),
    RoleBinding(
        id="rbac-004",
        principal_type="user",
        principal_id="triager@example.com",
        role=ROLE_INCIDENT_TRIAGER,
        platform_id="platform-001",
        state="active",
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    ),
    RoleBinding(
        id="rbac-005",
        principal_type="user",
        principal_id="owner@example.com",
        role=ROLE_SERVICE_OWNER,
        platform_id="platform-002",
        state="active",
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    ),
)

_LOCAL_RBAC_SERVICE = LocalRBACService()


def get_rbac_service() -> LocalRBACService:
    return _LOCAL_RBAC_SERVICE
