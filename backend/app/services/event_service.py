"""Event persistence and query service."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventFactor, Camera
from app.engines.event_types import EventCandidate
from app.models.enums import EventType, RiskLevel


async def upsert_event(
    db: AsyncSession,
    candidate: EventCandidate,
    risk_score: Optional[int] = None,
    risk_level: Optional[RiskLevel] = None,
    factors: Optional[List[dict]] = None,
) -> Event:
    """Create or update event by correlation_key."""
    stmt = select(Event).where(Event.correlation_key == candidate.correlation_key)
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()

    if event:
        event.window_end = candidate.window_end
        event.payload = {**event.payload, **candidate.payload}
        if risk_score is not None:
            event.risk_score = risk_score
        if risk_level is not None:
            event.risk_level = risk_level
    else:
        event = Event(
            camera_id=candidate.camera_id,
            event_type=candidate.event_type,
            language_key=candidate.language_key,
            correlation_key=candidate.correlation_key,
            window_start=candidate.window_start,
            window_end=candidate.window_end,
            location=to_point(candidate.geometry),
            risk_score=risk_score,
            risk_level=risk_level,
            payload=candidate.payload,
            alertable=candidate.alertable,
        )
        db.add(event)

    await db.commit()
    await db.refresh(event)

    # Persist factors
    if factors:
        for f in factors:
            db.add(EventFactor(
                event_id=event.id,
                code=f["code"],
                delta=f["delta"],
                reason=f["reason"],
            ))
        await db.commit()

    return event


async def find_recent_by_correlation_key(
    db: AsyncSession,
    correlation_key: str,
    minutes: int = 5,
) -> Optional[Event]:
    """Find recent event with same correlation key."""
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    stmt = select(Event).where(
        Event.correlation_key == correlation_key,
        Event.created_at >= cutoff,
    ).order_by(Event.created_at.desc())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_events(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    camera_id: Optional[UUID] = None,
    event_type: Optional[str] = None,
    alertable: Optional[bool] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
) -> tuple[list[Event], int]:
    stmt = select(Event)
    if camera_id:
        stmt = stmt.where(Event.camera_id == camera_id)
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    if alertable is not None:
        stmt = stmt.where(Event.alertable == alertable)
    if from_ts:
        stmt = stmt.where(Event.created_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Event.created_at <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Event.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


def to_point(geometry: tuple[float, float]):
    """Convert (lon, lat) to WKTElement."""
    from geoalchemy2 import WKTElement
    return WKTElement(f"POINT({geometry[0]} {geometry[1]})", srid=4326)