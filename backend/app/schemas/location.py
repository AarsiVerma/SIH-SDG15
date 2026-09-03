"""Location schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LocationCreate(BaseModel):
    lat: float
    lon: float
    captured_at: datetime
    source: str = "simulated"


class LocationRead(BaseModel):
    id: UUID
    ranger_id: UUID
    captured_at: datetime
    geom: dict  # GeoJSON Point
    source: str

    model_config = ConfigDict(from_attributes=True)


class RangerLocationRead(BaseModel):
    id: UUID
    ranger_id: UUID
    captured_at: datetime
    geom: dict
    source: str

    model_config = ConfigDict(from_attributes=True)