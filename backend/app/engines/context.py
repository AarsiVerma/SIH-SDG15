"""ContextProvider and SceneContext."""
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol, Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import functions as geofunc
from geoalchemy2 import Geography

from app.db.session import get_session
from app.models import Zone, Camera, Ranger, RangerLocation, Track
from app.models.enums import ZoneType
from app.core.config import get_settings


@dataclass
class SceneContext:
    camera_id: UUID
    timestamp: datetime
    zone_ids: List[UUID]
    in_restricted: bool
    is_night: bool
    nearby_ranger_ids: List[UUID]
    nearby_wildlife_track_ids: List[UUID]
    camera_online: bool


class ContextProvider(Protocol):
    def for_camera(self, camera_id: UUID, timestamp: datetime) -> SceneContext: ...


class PostGISContextProvider:
    """ContextProvider using PostGIS for spatial queries."""

    def __init__(self, settings=None):
        self.settings = settings or get_settings()

    async def for_camera(self, camera_id: UUID, timestamp: datetime) -> SceneContext:
        async for session in get_session():
            return await self._build_context(session, camera_id, timestamp)

    async def _build_context(
        self,
        session: AsyncSession,
        camera_id: UUID,
        timestamp: datetime,
    ) -> SceneContext:
        # Get camera
        camera = await session.get(Camera, camera_id)
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")

        # Zones containing camera point
        zone_stmt = select(Zone.id).where(
            Zone.forest_id == camera.forest_id,
            geofunc.ST_Contains(Zone.geom, camera.location),
        )
        zone_ids = [row[0] for row in (await session.execute(zone_stmt)).all()]

        # Check if any zone is restricted
        restricted_stmt = select(Zone.id).where(
            Zone.forest_id == camera.forest_id,
            Zone.is_restricted == True,
            geofunc.ST_Contains(Zone.geom, camera.location),
        )
        in_restricted = (await session.execute(restricted_stmt)).scalar_one_or_none() is not None

        # Night check
        is_night = self._is_night(timestamp)

        # Nearby rangers (latest location per ranger within radius and time skew)
        nearby_rangers = await self._nearby_rangers(session, camera, timestamp)

        # Nearby wildlife tracks (animal class, same camera, recent)
        wildlife_tracks = await self._nearby_wildlife(session, camera, timestamp)

        # Camera health
        from app.models import CameraHealth
        health = await session.get(CameraHealth, camera_id)
        camera_online = health.state == "online" if health else False

        return SceneContext(
            camera_id=camera_id,
            timestamp=timestamp,
            zone_ids=zone_ids,
            in_restricted=in_restricted,
            is_night=is_night,
            nearby_ranger_ids=nearby_rangers,
            nearby_wildlife_track_ids=wildlife_tracks,
            camera_online=camera_online,
        )

    def _is_night(self, timestamp: datetime) -> bool:
        """Check if timestamp falls in night window."""
        try:
            ns = time.fromisoformat(self.settings.night_start)
            ne = time.fromisoformat(self.settings.night_end)
        except ValueError:
            return False

        t = timestamp.time()
        if ns < ne:
            return ns <= t < ne
        else:  # crosses midnight
            return t >= ns or t < ne

    async def _nearby_rangers(
        self,
        session: AsyncSession,
        camera: Camera,
        timestamp: datetime,
    ) -> List[UUID]:
        """Rangers within radius whose latest location is within time skew."""
        from sqlalchemy import func as sa_func

        # Subquery: latest location per ranger
        latest_subq = (
            select(
                RangerLocation.ranger_id,
                sa_func.max(RangerLocation.captured_at).label("latest_at")
            )
            .where(RangerLocation.captured_at >= timestamp - self.settings.ranger_location_skew)
            .group_by(RangerLocation.ranger_id)
            .subquery()
        )

        stmt = select(RangerLocation.ranger_id).join(
            latest_subq,
            (RangerLocation.ranger_id == latest_subq.c.ranger_id) &
            (RangerLocation.captured_at == latest_subq.c.latest_at)
        ).where(
            geofunc.ST_DWithin(
                RangerLocation.geom.cast(Geography),
                camera.location.cast(Geography),
                self.settings.ranger_proximity_radius_m,
            ),
            RangerLocation.ranger_id.in_(
                select(Ranger.id).where(Ranger.active == True)
            )
        )
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]

    async def _nearby_wildlife(
        self,
        session: AsyncSession,
        camera: Camera,
        timestamp: datetime,
    ) -> List[UUID]:
        """Animal tracks on same camera within recent window."""
        from datetime import timedelta
        window = timestamp - timedelta(seconds=30)  # configurable

        stmt = select(Track.id).where(
            Track.camera_id == camera.id,
            Track.class_name == "animal",
            Track.last_seen >= window,
            Track.status == "active",
        )
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]