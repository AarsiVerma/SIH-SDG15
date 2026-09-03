"""Fire events API."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.models import Event, Ranger, Camera
from app.models.enums import EventType
from app.schemas.fire import FireEventRead, NearbyAssetRead
from app.schemas.common import Page

router = APIRouter(prefix="/fire", tags=["fire"])


@router.get("/events", response_model=Page[FireEventRead])
async def list_fire_events(
    pagination: Pagination,
    severity: Optional[str] = Query(None),
    camera_id: Optional[UUID] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event).where(Event.event_type.in_([EventType.FIRE_DETECTED, EventType.SMOKE_DETECTED]))
    if camera_id:
        stmt = stmt.where(Event.camera_id == camera_id)
    if from_ts:
        stmt = stmt.where(Event.created_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Event.created_at <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Event.created_at.desc()).limit(pagination.limit).offset(pagination.offset)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    # Convert to FireEventRead
    fire_events = []
    for e in items:
        fire_events.append(FireEventRead(
            id=e.id,
            camera_id=e.camera_id,
            event_type=e.event_type,
            severity=e.payload.get("severity", "unknown"),
            location={"type": "Point", "coordinates": [float(e.location.x), float(e.location.y)]},
            created_at=e.created_at,
        ))

    return Page(items=fire_events, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/events/{event_id}/nearby", response_model=List[NearbyAssetRead])
async def get_nearby_assets(
    event_id: UUID,
    radius_m: int = Query(5000),
    db: AsyncSession = Depends(get_db),
):
    event = await db.get(Event, event_id)
    if not event:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Event not found")

    from geoalchemy2 import func as geofunc
    from geoalchemy2 import Geography

    assets = []

    # Nearby rangers
    ranger_stmt = select(Ranger.id, Ranger.name, RangerLocation.geom).join(
        RangerLocation, Ranger.id == RangerLocation.ranger_id
    ).where(
        geofunc.ST_DWithin(
            RangerLocation.geom.cast(Geography),
            event.location.cast(Geography),
            radius_m,
        )
    )
    ranger_result = await db.execute(ranger_stmt)
    for r_id, r_name, r_geom in ranger_result:
        assets.append(NearbyAssetRead(
            type="ranger",
            id=r_id,
            name=r_name,
            location={"type": "Point", "coordinates": [float(r_geom.x), float(r_geom.y)]},
        ))

    # Nearby cameras
    cam_stmt = select(Camera.id, Camera.name, Camera.location).where(
        geofunc.ST_DWithin(
            Camera.location.cast(Geography),
            event.location.cast(Geography),
            radius_m,
        )
    )
    cam_result = await db.execute(cam_stmt)
    for c_id, c_name, c_geom in cam_result:
        assets.append(NearbyAssetRead(
            type="camera",
            id=c_id,
            name=c_name,
            location={"type": "Point", "coordinates": [float(c_geom.x), float(c_geom.y)]},
        ))

    return assets