"""Incident outcomes API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models import Incident, IncidentOutcomeRecord
from app.models.enums import IncidentOutcome, IncidentStatus
from app.schemas.incident import IncidentOutcomeRead, IncidentOutcomeCreate

router = APIRouter(prefix="/incidents", tags=["outcomes"])


@router.post("/{incident_id}/outcome", response_model=IncidentOutcomeRead, status_code=status.HTTP_201_CREATED)
async def create_outcome(
    incident_id: UUID,
    data: IncidentOutcomeCreate,
    db: AsyncSession = Depends(get_db),
):
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status != IncidentStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Outcome can only be set on CLOSED incidents")

    existing = await db.execute(
        select(IncidentOutcomeRecord).where(IncidentOutcomeRecord.incident_id == incident_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Outcome already recorded")

    outcome = IncidentOutcomeRecord(
        incident_id=incident_id,
        outcome=data.outcome,
        notes=data.notes,
        decided_by_user_id=data.decided_by_user_id,
    )
    db.add(outcome)
    await db.commit()
    await db.refresh(outcome)
    return outcome


@router.get("/{incident_id}/outcome", response_model=IncidentOutcomeRead)
async def get_outcome(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(IncidentOutcomeRecord).where(IncidentOutcomeRecord.incident_id == incident_id)
    result = await db.execute(stmt)
    outcome = result.scalar_one_or_none()
    if not outcome:
        raise HTTPException(status_code=404, detail="Outcome not recorded")
    return outcome


@router.get("/analytics/false-positive-rate")
async def false_positive_rate(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)

    total_stmt = select(func.count(IncidentOutcomeRecord.id)).where(IncidentOutcomeRecord.decided_at >= cutoff)
    total = (await db.execute(total_stmt)).scalar_one()

    fp_stmt = select(func.count(IncidentOutcomeRecord.id)).where(
        IncidentOutcomeRecord.decided_at >= cutoff,
        IncidentOutcomeRecord.outcome == IncidentOutcome.FALSE_POSITIVE,
    )
    fp = (await db.execute(fp_stmt)).scalar_one()

    return {
        "period_days": days,
        "total_closed": total,
        "false_positives": fp,
        "false_positive_rate": fp / total if total > 0 else 0.0,
    }