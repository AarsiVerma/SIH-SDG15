"""Camera health API."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import CameraHealth
from app.models.enums import CameraHealthState
from app.schemas.camera_health import CameraHealthRead
from app.services.health_service import list_camera_health

router = APIRouter(prefix="/cameras", tags=["camera-health"])


@router.get("/health", response_model=List[CameraHealthRead])
async def get_camera_health(
    limit: int = 100,
    offset: int = 0,
    state: Optional[CameraHealthState] = None,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    stmt = select(CameraHealth)
    if state:
        stmt = stmt.where(CameraHealth.state == state)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())