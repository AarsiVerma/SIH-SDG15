"""Ranger schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RangerBase(BaseModel):
    badge_code: str
    name: str
    is_simulated: bool = False
    active: bool = True


class RangerCreate(RangerBase):
    pass


class RangerUpdate(BaseModel):
    name: str | None = None
    is_simulated: bool | None = None
    active: bool | None = None


class RangerRead(RangerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)