"""Incident API."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.incident import IncidentRead, IncidentDetail, TransitionRequest, AssignRequest, NoteRequest
from app.schemas.common import Page
from app.services.incident_service import (
    list_incidents, get_incident, transition_incident, assign_incident, add_incident_note, get_incident_history,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=Page[IncidentRead])
async def list_incidents_endpoint(
    pagination: Pagination,
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    camera_id: Optional[UUID] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_incidents(
        db, pagination.limit, pagination.offset,
        status=status, risk_level=risk_level,
        camera_id=camera_id, from_ts=from_ts, to_ts=to_ts
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/{incident_id}", response_model=IncidentDetail)
async def get_incident_endpoint(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    incident = await get_incident(db, incident_id)
    if not incident:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Incident not found")
    return incident


@router.post("/{incident_id}/transition")
async def transition_incident_endpoint(
    incident_id: UUID,
    data: TransitionRequest,
    db: AsyncSession = Depends(get_db),
):
    incident = await transition_incident(db, incident_id, data.to_status, data.note)
    return incident


@router.post("/{incident_id}/assign")
async def assign_incident_endpoint(
    incident_id: UUID,
    data: AssignRequest,
    db: AsyncSession = Depends(get_db),
):
    incident = await assign_incident(db, incident_id, data.user_id, data.ranger_id)
    return incident


@router.post("/{incident_id}/notes")
async def add_note_endpoint(
    incident_id: UUID,
    data: NoteRequest,
    db: AsyncSession = Depends(get_db),
):
    incident = await add_incident_note(db, incident_id, data.note)
    return incident


@router.get("/{incident_id}/history")
async def get_history_endpoint(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    from app.services.incident_service import get_incident_history
    history = await get_incident_history(db, incident_id)
    return history