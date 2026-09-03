"""Camera health schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict

from pydantic import BaseModel, ConfigDict

from app.models.enums import CameraHealthState


class CameraHealthRead(BaseModel):
    id: UUID
    camera_id: UUID
    state: CameraHealthState
    last_heartbeat: datetime | None
    last_frame_at: datetime | None
    last_detection_at: datetime | None
    notes: str | None
    extra: Dict

    model_config = ConfigDict(from_attributes=True)