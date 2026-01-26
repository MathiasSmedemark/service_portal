"""Repository dependency providers."""

from __future__ import annotations

from app.db.fixtures import LocalFixtureRepository

_LOCAL_REPOSITORY = LocalFixtureRepository()


def get_repository() -> LocalFixtureRepository:
    return _LOCAL_REPOSITORY
