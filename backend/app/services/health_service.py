"""Camera health service."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import CameraHealth, Camera
from app.models.enums import CameraHealthState


class CameraHealthMonitor:
    """Tracks camera online/offline/degraded state."""

    def __init__(self, offline_after: int = 30):
        self.offline_after = offline_after  # seconds

    async def observe_frame(self, db: AsyncSession, camera_id: UUID) -> None:
        """Called when a frame is successfully read."""
        await self._update_health(db, camera_id, frame=True)

    async def observe_heartbeat(self, db: AsyncSession, camera_id: UUID) -> None:
        """Called on explicit heartbeat."""
        await self._update_health(db, camera_id, heartbeat=True)

    async def observe_detection(self, db: AsyncSession, camera_id: UUID) -> None:
        """Called when detections are produced."""
        await self._update_health(db, camera_id, detection=True)

    async def observe_error(self, db: AsyncSession, camera_id: UUID, error: str) -> None:
        """Called on pipeline error."""
        health = await self._get_or_create(db, camera_id)
        health.state = CameraHealthState.DEGRADED
        health.notes = error[:500]
        await db.commit()

    async def _update_health(
        self,
        db: AsyncSession,
        camera_id: UUID,
        frame: bool = False,
        heartbeat: bool = False,
        detection: bool = False,
    ) -> None:
        health = await self._get_or_create(db, camera_id)
        now = datetime.utcnow()

        if frame:
            health.last_frame_at = now
        if heartbeat:
            health.last_heartbeat = now
        if detection:
            health.last_detection_at = now

        # Determine state
        if health.last_frame_at and (now - health.last_frame_at).total_seconds() < self.offline_after:
            health.state = CameraHealthState.ONLINE
        elif health.last_frame_at:
            health.state = CameraHealthState.OFFLINE
        else:
            health.state = CameraHealthState.UNKNOWN

        await db.commit()

    async def _get_or_create(self, db: AsyncSession, camera_id: UUID) -> CameraHealth:
        health = await db.get(CameraHealth, camera_id)
        if not health:
            health = CameraHealth(camera_id=camera_id)
            db.add(health)
        return health


async def classify_health(
    last_frame: Optional[datetime],
    last_heartbeat: Optional[datetime],
    last_detection: Optional[datetime],
    job_running: bool,
    offline_after: int = 30,
) -> tuple[str, str]:
    """Classify camera health state with reason code."""
    now = datetime.utcnow()

    if not job_running:
        return CameraHealthState.OFFLINE.value, "not_ingesting"

    if last_frame and (now - last_frame).total_seconds() <= offline_after:
        if last_detection:
            return CameraHealthState.ONLINE.value, "active"
        return CameraHealthState.ONLINE.value, "no_activity"

    return CameraHealthState.OFFLINE.value, "pipeline_stall"


async def list_camera_health(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[CameraHealth]:
    stmt = select(CameraHealth).order_by(CameraHealth.camera_id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())