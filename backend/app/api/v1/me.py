"""User identity endpoint."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, status

from app.auth.deps import get_current_user
from app.auth.identity import Identity

router = APIRouter(prefix="/api/v1")


@router.get("/me", status_code=status.HTTP_200_OK)
def read_me(identity: Identity = Depends(get_current_user)) -> dict:
    return asdict(identity)
