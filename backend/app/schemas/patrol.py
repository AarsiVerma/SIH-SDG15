"""Patrol schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PatrolBase(BaseModel):
    ranger_id: UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "active"


class PatrolCreate(PatrolBase):
    pass


class PatrolUpdate(BaseModel):
    ended_at: Optional[datetime] = None
    status: Optional[str] = None
    route_geom: Optional[dict] = None


class PatrolRead(PatrolBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)