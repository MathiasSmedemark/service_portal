"""Middleware for request context (request id + identity)."""

from __future__ import annotations

import os
import uuid
from typing import Callable

from fastapi import Request, Response

from app.auth.identity import extract_identity


def _get_request_id(request: Request) -> str:
    return request.headers.get("X-Request-Id") or str(uuid.uuid4())


async def request_context_middleware(request: Request, call_next: Callable) -> Response:
    request_id = _get_request_id(request)
    request.state.request_id = request_id
    request.state.identity = extract_identity(request.headers, os.environ)

    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
