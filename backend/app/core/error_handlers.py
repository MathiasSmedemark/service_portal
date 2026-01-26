"""FastAPI error handlers with standard response shape."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError

HTTP_422_UNPROCESSABLE = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)


def _error_payload(code: str, message: str, request_id: Optional[str]) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def _get_request_id(request: Request) -> Optional[str]:
    return getattr(request.state, "request_id", None)


def _http_error_code(status_code: int) -> str:
    if status_code == status.HTTP_404_NOT_FOUND:
        return "not_found"
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "unauthorized"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "forbidden"
    if status_code == status.HTTP_409_CONFLICT:
        return "conflict"
    if status_code == HTTP_422_UNPROCESSABLE:
        return "validation_error"
    return "http_error"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = _get_request_id(request)
        response = JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = _get_request_id(request)
        code = _http_error_code(exc.status_code)
        response = JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(code, str(exc.detail), request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = _get_request_id(request)
        response = JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE,
            content=_error_payload("validation_error", "Validation error", request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = _get_request_id(request)
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("internal_error", "Internal server error", request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response
