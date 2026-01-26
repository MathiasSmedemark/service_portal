"""FastAPI entrypoint and wiring."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api.v1.catalog import router as catalog_router
from .api.v1.health import router as health_router
from .auth.middleware import request_context_middleware


def _error_payload(code: str, message: str, request_id: Optional[str]) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def create_app() -> FastAPI:
    app = FastAPI(title="Service Portal")
    app.middleware("http")(request_context_middleware)

    app.include_router(health_router)
    app.include_router(catalog_router)
    _mount_spa(app)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        response = JSONResponse(
            status_code=exc.status_code,
            content=_error_payload("http_error", str(exc.detail), request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("internal_error", "Internal server error", request_id),
        )
        if request_id:
            response.headers["X-Request-Id"] = request_id
        return response

    return app


def _mount_spa(app: FastAPI) -> None:
    app_dir = Path(__file__).resolve().parent
    repo_root = app_dir.parents[1]
    candidates = [
        app_dir / "static",
        repo_root / "frontend" / "dist",
    ]

    for candidate in candidates:
        if (candidate / "index.html").is_file():
            app.mount("/", StaticFiles(directory=str(candidate), html=True), name="spa")
            return


app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("DATABRICKS_APP_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
