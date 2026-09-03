"""Wildlife schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WildlifeObservationRead(BaseModel):
    id: UUID
    track_id: UUID
    camera_id: UUID
    species: str
    count_estimate: int
    first_seen: datetime
    last_seen: datetime
    location: dict  # GeoJSON Point

    model_config = ConfigDict(from_attributes=True)