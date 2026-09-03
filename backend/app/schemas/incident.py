"""Incident schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.enums import IncidentStatus, RiskLevel, IncidentOutcome
from app.schemas.event import EventRead
from app.schemas.evidence import EvidenceRead  # forward ref


class IncidentBase(BaseModel):
    public_id: str
    title: str
    language_key: str
    status: IncidentStatus
    risk_score: int | None
    risk_level: RiskLevel | None
    location: dict  # GeoJSON Point
    assigned_user_id: UUID | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime


class IncidentRead(IncidentBase):
    id: UUID
    events: List[EventRead] = []
    evidence: List[EvidenceRead] = []

    model_config = ConfigDict(from_attributes=True)


class IncidentDetail(IncidentRead):
    factors: List[dict] = []
    status_history: List[dict] = []


class TransitionRequest(BaseModel):
    to_status: IncidentStatus
    note: str | None = None


class AssignRequest(BaseModel):
    user_id: UUID | None = None
    ranger_id: UUID | None = None


class NoteRequest(BaseModel):
    note: str


class IncidentOutcomeCreate(BaseModel):
    outcome: IncidentOutcome
    notes: str | None = None
    decided_by_user_id: UUID | None = None


class IncidentOutcomeRead(BaseModel):
    id: UUID
    incident_id: UUID
    outcome: IncidentOutcome
    notes: str | None
    decided_by_user_id: UUID | None
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)