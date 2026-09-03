"""Camera schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

from app.models.enums import CameraStatus, SourceType


class CameraSourceCreate(BaseModel):
    source_type: SourceType
    uri: str = Field(..., max_length=1024)
    extra: dict = Field(default_factory=dict)


class CameraSourceRead(CameraSourceCreate):
    id: UUID
    camera_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CameraBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=64)
    forest_id: UUID | None = None
    location: dict  # GeoJSON Point
    heading_deg: float | None = None
    status: CameraStatus = CameraStatus.PLANNED
    is_simulated: bool = False


class CameraCreate(CameraBase):
    sources: list[CameraSourceCreate] = Field(default_factory=list)


class CameraUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    forest_id: UUID | None = None
    location: dict | None = None
    heading_deg: float | None = None
    status: CameraStatus | None = None
    is_simulated: bool | None = None


class CameraRead(CameraBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    sources: list[CameraSourceRead] = Field(default_factory=[])

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        data = {
            "id": obj.id,
            "name": obj.name,
            "code": obj.code,
            "forest_id": obj.forest_id,
            "location": {"type": "Point", "coordinates": [float(obj.location.x), float(obj.location.y)]} if obj.location else None,
            "heading_deg": obj.heading_deg,
            "status": obj.status,
            "is_simulated": obj.is_simulated,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
            "sources": [CameraSourceRead.model_validate(s) for s in obj.sources],
        }
        return cls(**data)