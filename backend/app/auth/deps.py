"""Auth dependencies for request identity."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import HTTPException, Request, status

from app.auth.identity import Identity, extract_identity


def get_optional_identity(request: Request) -> Optional[Identity]:
    identity = getattr(request.state, "identity", None)
    if identity is None:
        identity = extract_identity(request.headers, os.environ)
        request.state.identity = identity
    return identity


def get_current_identity(request: Request) -> Identity:
    identity = get_optional_identity(request)
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user identity",
        )
    return identity
