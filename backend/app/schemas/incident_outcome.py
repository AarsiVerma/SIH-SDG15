"""Incident outcome schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import IncidentOutcome


class IncidentOutcomeCreate(BaseModel):
    outcome: IncidentOutcome
    notes: Optional[str] = None
    decided_by_user_id: Optional[UUID] = None


class IncidentOutcomeRead(BaseModel):
    id: UUID
    incident_id: UUID
    outcome: IncidentOutcome
    notes: Optional[str]
    decided_by_user_id: Optional[UUID]
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)