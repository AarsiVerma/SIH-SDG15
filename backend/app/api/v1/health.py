"""Liveness and readiness probes."""
from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import db_available

router = APIRouter(tags=["health"])


@router.get("/live")
async def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict:
    """200 even when DB is down before VR-012 wiring; db flag reflects reality."""
    db_ok = await db_available() if get_settings().database_url else False
    return {"status": "ok" if db_ok else "degraded", "db": db_ok, "version": "0.1.0"}