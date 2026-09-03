"""Evidence persistence service."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Evidence, Incident, Event
from app.models.enums import EvidenceKind


async def create_evidence(
    db: AsyncSession,
    incident_id: Optional[UUID],
    event_id: UUID,
    camera_id: UUID,
    kind: EvidenceKind,
    storage_uri: str,
    sha256: str,
    captured_at: datetime,
    bbox_xyxy: dict,
    disclaimer_key: str,
) -> Evidence:
    evidence = Evidence(
        incident_id=incident_id,
        event_id=event_id,
        camera_id=camera_id,
        kind=kind,
        storage_uri=storage_uri,
        sha256=sha256,
        captured_at=captured_at,
        bbox_xyxy=bbox_xyxy,
        disclaimer_key=disclaimer_key,
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence


async def get_evidence(db: AsyncSession, evidence_id: UUID) -> Evidence | None:
    from sqlalchemy import select
    stmt = select(Evidence).where(Evidence.id == evidence_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_evidence(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    incident_id: Optional[UUID] = None,
    event_id: Optional[UUID] = None,
) -> list[Evidence]:
    from sqlalchemy import select, func
    stmt = select(Evidence)
    if incident_id:
        stmt = stmt.where(Evidence.incident_id == incident_id)
    if event_id:
        stmt = stmt.where(Evidence.event_id == event_id)

    stmt = stmt.order_by(Evidence.captured_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())