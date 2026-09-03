"""Track schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TrackRead(BaseModel):
    id: UUID
    camera_id: UUID
    local_track_id: int
    class_name: str
    first_seen: datetime
    last_seen: datetime
    confidence_avg: float
    status: str
    global_id: UUID | None

    model_config = ConfigDict(from_attributes=True)


class TrackPointRead(BaseModel):
    id: UUID
    track_id: UUID
    captured_at: datetime
    bbox_xyxy: dict
    centroid_image: dict
    map_point: dict | None

    model_config = ConfigDict(from_attributes=True)