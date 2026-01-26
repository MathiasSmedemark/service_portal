"""Logging configuration and request logging middleware."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, Mapping

from fastapi import Request, Response

from app.core.config import Settings

APP_LOGGER_NAME = "service_portal"
REQUEST_LOGGER_NAME = "service_portal.request"

_STANDARD_LOG_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


def _extract_extras(record: logging.LogRecord) -> Mapping[str, Any]:
    return {
        key: value
        for key, value in record.__dict__.items()
        if key not in _STANDARD_LOG_RECORD_ATTRS and value is not None
    }


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_extract_extras(record))
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=True)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        base = f"{timestamp} {record.levelname} {record.name}: {record.getMessage()}"
        extras = _extract_extras(record)
        if extras:
            suffix = " ".join(f"{key}={value}" for key, value in extras.items())
            return f"{base} {suffix}"
        return base


def _parse_log_level(value: str | None) -> int:
    if not value:
        return logging.INFO
    if value.isdigit():
        return int(value)
    level = logging.getLevelName(value.upper())
    return level if isinstance(level, int) else logging.INFO


def _resolve_log_format(settings: Settings) -> str:
    format_env = os.getenv("LOG_FORMAT", "").strip().lower()
    if format_env in {"json", "text"}:
        return format_env
    return "json" if settings.databricks_host else "text"


def configure_logging(settings: Settings) -> logging.Logger:
    logger = logging.getLogger(APP_LOGGER_NAME)
    level = _parse_log_level(os.getenv("LOG_LEVEL"))
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger

    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter: logging.Formatter
    if _resolve_log_format(settings) == "json":
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    request_logger = logging.getLogger(REQUEST_LOGGER_NAME)
    request_logger.setLevel(logging.NOTSET)
    request_logger.propagate = True

    return logger


async def request_logging_middleware(
    request: Request, call_next: Callable
) -> Response:
    logger = logging.getLogger(REQUEST_LOGGER_NAME)
    start = perf_counter()
    status_code = 500
    response: Response | None = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = (perf_counter() - start) * 1000
        identity = getattr(request.state, "identity", None)
        user = getattr(identity, "user", None) if identity else None
        request_id = getattr(request.state, "request_id", None)
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": round(latency_ms, 2),
                "request_id": request_id,
                "user": user,
            },
        )
