"""Incident service."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Incident, IncidentEvent, IncidentStatusHistory, Event,
    User, Ranger, Evidence, IncidentOutcomeRecord
)
from app.models.enums import IncidentStatus, RiskLevel
from app.engines.incident_state import validate_transition, can_transition
from app.schemas.incident import TransitionRequest, AssignRequest
from app.core.errors import AppError, ErrorCode


async def list_incidents(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    status: Optional[IncidentStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    camera_id: Optional[UUID] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
) -> tuple[list[Incident], int]:
    stmt = select(Incident)
    if status:
        stmt = stmt.where(Incident.status == status)
    if risk_level:
        stmt = stmt.where(Incident.risk_level == risk_level)
    if camera_id:
        stmt = stmt.join(IncidentEvent).join(Event).where(Event.camera_id == camera_id)
    if from_ts:
        stmt = stmt.where(Incident.created_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Incident.created_at <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Incident.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_incident(db: AsyncSession, incident_id: UUID) -> Incident | None:
    stmt = select(Incident).options(
        selectinload(Incident.events).selectinload(IncidentEvent.event),
        selectinload(Incident.evidence),
        selectinload(Incident.status_history),
    ).where(Incident.id == incident_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def transition_incident(
    db: AsyncSession,
    incident_id: UUID,
    to_status: IncidentStatus,
    note: Optional[str],
    actor_user_id: Optional[UUID] = None,
) -> Incident:
    incident = await get_incident(db, incident_id)
    if not incident:
        raise AppError(ErrorCode.NOT_FOUND, "Incident not found")

    # Validate transition (role check omitted for MVP)
    if not can_transition(incident.status, to_status, actor_user_id):
        raise AppError(ErrorCode.FORBIDDEN, f"Invalid transition: {incident.status} -> {to_status}")

    incident.status = to_status
    incident.updated_at = datetime.utcnow()

    db.add(IncidentStatusHistory(
        incident_id=incident.id,
        from_status=incident.status,
        to_status=to_status,
        actor_user_id=actor_user_id,
        note=note,
    ))

    await db.commit()
    await db.refresh(incident)
    return incident


async def assign_incident(
    db: AsyncSession,
    incident_id: UUID,
    user_id: Optional[UUID] = None,
    ranger_id: Optional[UUID] = None,
) -> Incident:
    incident = await get_incident(db, incident_id)
    if not incident:
        raise AppError(ErrorCode.NOT_FOUND, "Incident not found")

    if user_id:
        user = await db.get(User, user_id)
        if not user:
            raise AppError(ErrorCode.NOT_FOUND, "User not found")
        incident.assigned_user_id = user_id
    elif ranger_id:
        ranger = await db.get(Ranger, ranger_id)
        if not ranger:
            raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")
        # Would link via user.ranger_id in production

    await db.commit()
    await db.refresh(incident)
    return incident


async def add_incident_note(
    db: AsyncSession,
    incident_id: UUID,
    note: str,
    actor_user_id: Optional[UUID] = None,
) -> Incident:
    incident = await get_incident(db, incident_id)
    if not incident:
        raise AppError(ErrorCode.NOT_FOUND, "Incident not found")

    incident.resolution_notes = (incident.resolution_notes or "") + f"\n[{datetime.utcnow().isoformat()}] {note}"
    incident.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(incident)
    return incident


async def get_incident_history(db: AsyncSession, incident_id: UUID) -> List[IncidentStatusHistory]:
    stmt = select(IncidentStatusHistory).where(
        IncidentStatusHistory.incident_id == incident_id
    ).order_by(IncidentStatusHistory.at)
    result = await db.execute(stmt)
    return list(result.scalars().all())