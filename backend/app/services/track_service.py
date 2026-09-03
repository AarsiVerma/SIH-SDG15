"""Track persistence service."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Track, TrackPoint, Camera
from app.vision.tracker_base import TrackUpdate


async def upsert_track(
    db: AsyncSession,
    camera_id: UUID,
    local_track_id: int,
    class_name: str,
    first_seen: datetime,
    last_seen: datetime,
    confidence_avg: float,
    status: str = "active",
) -> Track:
    """Get or create track by camera_id + local_track_id."""
    stmt = select(Track).where(
        Track.camera_id == camera_id,
        Track.local_track_id == local_track_id,
    )
    result = await db.execute(stmt)
    track = result.scalar_one_or_none()

    if track:
        track.last_seen = last_seen
        track.confidence_avg = confidence_avg
        track.status = status
    else:
        track = Track(
            camera_id=camera_id,
            local_track_id=local_track_id,
            class_name=class_name,
            first_seen=first_seen,
            last_seen=last_seen,
            confidence_avg=confidence_avg,
            status=status,
        )
        db.add(track)

    await db.commit()
    await db.refresh(track)
    return track


async def append_track_points(
    db: AsyncSession,
    track_id: UUID,
    updates: list[TrackUpdate],
) -> list[TrackPoint]:
    """Append track points for a track."""
    created = []
    for u in updates:
        point = TrackPoint(
            track_id=track_id,
            captured_at=u.last_seen,
            bbox_xyxy={
                "x1": u.bbox_xyxy[0],
                "y1": u.bbox_xyxy[1],
                "x2": u.bbox_xyxy[2],
                "y2": u.bbox_xyxy[3],
            },
            centroid_image={"x": u.centroid[0], "y": u.centroid[1]},
            map_point=None,  # MVP: no homography
        )
        db.add(point)
        created.append(point)

    await db.commit()
    for p in created:
        await db.refresh(p)
    return created


async def list_tracks(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    camera_id: Optional[UUID] = None,
    active_only: bool = False,
) -> tuple[list[Track], int]:
    stmt = select(Track)
    if camera_id:
        stmt = stmt.where(Track.camera_id == camera_id)
    if active_only:
        stmt = stmt.where(Track.status == "active")

    from sqlalchemy import func
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Track.first_seen.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_track_points(
    db: AsyncSession,
    track_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[TrackPoint]:
    stmt = select(TrackPoint).where(TrackPoint.track_id == track_id).order_by(TrackPoint.captured_at)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())