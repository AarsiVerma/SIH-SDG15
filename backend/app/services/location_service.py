"""Location provider and service."""
from typing import Protocol, List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sa_func
from geoalchemy2 import functions as geofunc
from geoalchemy2 import Geography

from app.models import Ranger, RangerLocation
from app.core.errors import AppError, ErrorCode


class LocationProvider(Protocol):
    def ingest(self, ranger_id: UUID, point: tuple[float, float], captured_at: datetime, source: str) -> None: ...
    def latest(self) -> List[RangerLocation]: ...


class PostGISLocationProvider:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def ingest(
        self,
        ranger_id: UUID,
        point: tuple[float, float],
        captured_at: datetime,
        source: str = "simulated",
    ) -> None:
        async for session in self.session_factory():
            ranger = await session.get(Ranger, ranger_id)
            if not ranger:
                raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")

            from geoalchemy2 import WKTElement
            loc = RangerLocation(
                ranger_id=ranger_id,
                captured_at=captured_at,
                geom=WKTElement(f"POINT({point[0]} {point[1]})", srid=4326),
                source=source,
            )
            session.add(loc)
            await session.commit()

    async def latest(self) -> List[RangerLocation]:
        async for session in self.session_factory():
            stmt = (
                select(RangerLocation)
                .distinct(RangerLocation.ranger_id)
                .order_by(RangerLocation.ranger_id, RangerLocation.captured_at.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())


async def ingest_location(
    db: AsyncSession,
    ranger_id: UUID,
    lat: float,
    lon: float,
    captured_at: datetime,
    source: str = "simulated",
) -> RangerLocation:
    ranger = await db.get(Ranger, ranger_id)
    if not ranger:
        raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")

    from geoalchemy2 import WKTElement
    loc = RangerLocation(
        ranger_id=ranger_id,
        captured_at=captured_at,
        geom=WKTElement(f"POINT({lon} {lat})", srid=4326),
        source=source,
    )
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def latest_locations(db: AsyncSession) -> List[RangerLocation]:
    stmt = (
        select(RangerLocation)
        .distinct(RangerLocation.ranger_id)
        .order_by(RangerLocation.ranger_id, RangerLocation.captured_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())