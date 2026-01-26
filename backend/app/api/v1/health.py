"""Health and readiness endpoints."""

from fastapi import APIRouter, status

router = APIRouter(prefix="/api/v1")


@router.get("/healthz", status_code=status.HTTP_200_OK)
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
def readyz() -> dict:
    # Stubbed readiness check; will be expanded with real checks later.
    return {"status": "ok", "ready": True}
