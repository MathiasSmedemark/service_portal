"""FastAPI entrypoint and wiring."""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.v1.catalog import router as catalog_router
from .api.v1.health import router as health_router
from .api.v1.me import router as me_router
from .auth.middleware import request_context_middleware
from .core.config import get_settings
from .core.error_handlers import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Service Portal")
    app.middleware("http")(request_context_middleware)
    register_error_handlers(app)

    app.include_router(health_router)
    app.include_router(catalog_router)
    app.include_router(me_router)
    _mount_spa(app)

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

    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.databricks_app_port)
