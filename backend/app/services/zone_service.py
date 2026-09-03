"""Zone and Forest service."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement

from app.models import Zone, ForestArea, ZoneType
from app.schemas.zone import ZoneCreate, ZoneUpdate, ForestCreate
from app.core.errors import AppError, ErrorCode


async def list_zones(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    forest_id: Optional[UUID] = None,
    restricted: Optional[bool] = None,
) -> tuple[list[Zone], int]:
    stmt = select(Zone)
    if forest_id:
        stmt = stmt.where(Zone.forest_id == forest_id)
    if restricted is not None:
        stmt = stmt.where(Zone.is_restricted == restricted)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Zone.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_zone(db: AsyncSession, zone_id: UUID) -> Zone | None:
    stmt = select(Zone).where(Zone.id == zone_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_zone(db: AsyncSession, data: ZoneCreate) -> Zone:
    coords = data.geom.get("coordinates")
    if not coords or not isinstance(coords[0], list):
        raise AppError(ErrorCode.VALIDATION_ERROR, "geom must be GeoJSON Polygon")
    # Flatten first ring
    ring = coords[0]
    wkt = "POLYGON((" + ", ".join(f"{c[0]} {c[1]}" for c in ring) + "))"
    poly = WKTElement(wkt, srid=4326)

    zone = Zone(
        forest_id=data.forest_id,
        name=data.name,
        zone_type=data.zone_type,
        is_restricted=data.is_restricted,
        geom=poly,
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


async def update_zone(db: AsyncSession, zone_id: UUID, data: ZoneUpdate) -> Zone | None:
    zone = await get_zone(db, zone_id)
    if not zone:
        return None

    if data.name is not None:
        zone.name = data.name
    if data.zone_type is not None:
        zone.zone_type = data.zone_type
    if data.is_restricted is not None:
        zone.is_restricted = data.is_restricted
    if data.geom is not None:
        coords = data.geom.get("coordinates")
        if coords and isinstance(coords[0], list):
            ring = coords[0]
            wkt = "POLYGON((" + ", ".join(f"{c[0]} {c[1]}" for c in ring) + "))"
            zone.geom = WKTElement(wkt, srid=4326)

    await db.commit()
    await db.refresh(zone)
    return zone


async def list_forests(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[ForestArea], int]:
    stmt = select(ForestArea)
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()
    stmt = stmt.order_by(ForestArea.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_forest(db: AsyncSession, data: ForestCreate) -> ForestArea:
    coords = data.geom.get("coordinates")
    if not coords or not isinstance(coords[0], list):
        raise AppError(ErrorCode.VALIDATION_ERROR, "geom must be GeoJSON Polygon")
    ring = coords[0]
    wkt = "POLYGON((" + ", ".join(f"{c[0]} {c[1]}" for c in ring) + "))"
    poly = WKTElement(wkt, srid=4326)

    forest = ForestArea(name=data.name, geom=poly)
    db.add(forest)
    await db.commit()
    await db.refresh(forest)
    return forest