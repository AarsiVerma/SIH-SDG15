"""Authorized ranger presence helper for risk factors."""
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import func as geofunc
from geoalchemy2 import Geography

from app.db.session import get_session
from app.models import Ranger, RangerLocation
from app.core.config import get_settings


async def rangers_near_camera(
    camera_id: UUID,
    at: datetime,
    radius_m: Optional[float] = None,
) -> List[UUID]:
    """Return ranger IDs near a camera at a given time."""
    settings = get_settings()
    radius = radius_m or settings.ranger_proximity_radius_m
    time_skew = timedelta(minutes=settings.ranger_location_skew_minutes)

    async for session in get_session():
        # Get camera location
        from app.models import Camera
        camera = await session.get(Camera, camera_id)
        if not camera:
            return []

        # Latest location per ranger within time skew
        latest_subq = (
            select(
                RangerLocation.ranger_id,
                sa_func.max(RangerLocation.captured_at).label("latest_at")
            )
            .where(RangerLocation.captured_at >= at - time_skew)
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
                radius,
            ),
            RangerLocation.ranger_id.in_(
                select(Ranger.id).where(Ranger.active == True)
            )
        )
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]