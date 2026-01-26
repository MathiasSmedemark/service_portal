"""RBAC service and permission helper tests."""

from app.auth.identity import Identity
from app.auth.permissions import require_roles
from app.services.rbac_service import (
    LocalRBACService,
    RoleBinding,
    ROLE_ADMIN,
    ROLE_CONTRIBUTOR,
    ROLE_VIEWER,
)


def _binding(
    binding_id: str,
    principal_id: str,
    role: str,
    platform_id: str | None,
    state: str = "active",
) -> RoleBinding:
    return RoleBinding(
        id=binding_id,
        principal_type="user",
        principal_id=principal_id,
        role=role,
        platform_id=platform_id,
        state=state,
        created_at="2024-07-12T09:00:00Z",
        created_by="seed",
        updated_at="2024-07-12T09:00:00Z",
        updated_by="seed",
    )


def test_local_rbac_service_resolves_mock_roles() -> None:
    rbac = LocalRBACService()
    identity = Identity(
        user="devuser",
        email="dev@example.com",
        preferred_username=None,
        source="dev",
    )

    roles = rbac.get_roles(identity)

    assert ROLE_ADMIN in roles
    assert rbac.has_role(identity, ROLE_ADMIN)


def test_local_rbac_service_filters_platform_roles() -> None:
    bindings = (
        _binding("rbac-101", "alice", ROLE_VIEWER, None),
        _binding("rbac-102", "alice", ROLE_CONTRIBUTOR, "platform-001"),
        _binding("rbac-103", "alice", ROLE_ADMIN, "platform-002"),
    )
    rbac = LocalRBACService(bindings=bindings)
    identity = Identity(user="alice", email=None, preferred_username=None, source="forwarded")

    roles = rbac.get_roles(identity, platform_id="platform-001")

    assert roles == {ROLE_VIEWER, ROLE_CONTRIBUTOR}


def test_permission_dependency_reports_granted() -> None:
    bindings = (
        _binding("rbac-201", "alice", ROLE_VIEWER, None),
        _binding("rbac-202", "alice", ROLE_CONTRIBUTOR, "platform-001"),
    )
    rbac = LocalRBACService(bindings=bindings)
    identity = Identity(user="alice", email=None, preferred_username=None, source="forwarded")

    dependency = require_roles(ROLE_CONTRIBUTOR, platform_id="platform-001")
    context = dependency(identity=identity, rbac=rbac)

    assert context.granted is True
    assert ROLE_CONTRIBUTOR in context.roles

    denied = require_roles(ROLE_ADMIN, platform_id="platform-001")(identity=identity, rbac=rbac)
    assert denied.granted is False
