"""Fire schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FireEventRead(BaseModel):
    id: UUID
    camera_id: UUID
    event_type: str
    severity: str
    location: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NearbyAssetRead(BaseModel):
    type: str  # ranger|camera
    id: UUID
    name: str
    location: dict

    model_config = ConfigDict(from_attributes=True)