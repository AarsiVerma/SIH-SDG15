"""Event schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models.enums import EventType, RiskLevel


class EventFactorRead(BaseModel):
    code: str
    delta: int
    reason: str

    model_config = ConfigDict(from_attributes=True)


class EventRead(BaseModel):
    id: UUID
    camera_id: UUID
    event_type: EventType
    language_key: str
    correlation_key: str
    window_start: datetime
    window_end: datetime
    location: dict  # GeoJSON Point
    risk_score: int | None
    risk_level: RiskLevel | None
    payload: dict
    alertable: bool
    created_at: datetime
    factors: List[EventFactorRead] = []

    model_config = ConfigDict(from_attributes=True)