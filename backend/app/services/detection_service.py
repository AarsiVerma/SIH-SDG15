"""Detection persistence service."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Detection, Camera
from app.vision.types import DetectionCandidate
from app.sources.base import Frame


async def persist_detections(
    db: AsyncSession,
    frame: Frame,
    candidates: list[DetectionCandidate],
) -> list[Detection]:
    """Persist detections for a frame. Returns created Detection objects."""
    created = []
    for c in candidates:
        det = Detection(
            camera_id=frame.camera_id,
            frame_seq=frame.seq,
            captured_at=frame.captured_at,
            class_name=c.class_name,
            class_id=c.class_id,
            confidence=c.confidence,
            bbox_xyxy={
                "x1": c.bbox_xyxy[0],
                "y1": c.bbox_xyxy[1],
                "x2": c.bbox_xyxy[2],
                "y2": c.bbox_xyxy[3],
            },
            centroid=None,  # Could compute from bbox if needed
            track_id=None,
            detector_id=c.detector_id,
            model_version=c.model_version,
        )
        db.add(det)
        created.append(det)

    if created:
        await db.commit()
        for d in created:
            await db.refresh(d)

    return created


async def list_detections(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    camera_id: Optional[UUID] = None,
    class_name: Optional[str] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
) -> tuple[list[Detection], int]:
    stmt = select(Detection)
    if camera_id:
        stmt = stmt.where(Detection.camera_id == camera_id)
    if class_name:
        stmt = stmt.where(Detection.class_name == class_name)
    if from_ts:
        stmt = stmt.where(Detection.captured_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Detection.captured_at <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Detection.captured_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total