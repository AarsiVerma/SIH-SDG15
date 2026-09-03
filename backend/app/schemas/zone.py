"""Zone and Forest schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import ZoneType


class ZoneBase(BaseModel):
    name: str = Field(..., max_length=255)
    zone_type: ZoneType = ZoneType.OTHER
    is_restricted: bool = False
    geom: dict  # GeoJSON Polygon


class ZoneCreate(ZoneBase):
    forest_id: UUID


class ZoneUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    zone_type: ZoneType | None = None
    is_restricted: bool | None = None
    geom: dict | None = None


class ZoneRead(ZoneBase):
    id: UUID
    forest_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        from geoalchemy2.shape import to_shape
        geom = to_shape(obj.geom) if obj.geom else None
        coords = list(geom.exterior.coords) if geom else None
        data = {
            "id": obj.id,
            "forest_id": obj.forest_id,
            "name": obj.name,
            "zone_type": obj.zone_type,
            "is_restricted": obj.is_restricted,
            "geom": {"type": "Polygon", "coordinates": [coords]} if coords else None,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class ForestBase(BaseModel):
    name: str = Field(..., max_length=255)
    geom: dict  # GeoJSON Polygon


class ForestCreate(ForestBase):
    pass


class ForestRead(ForestBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        from geoalchemy2.shape import to_shape
        geom = to_shape(obj.geom) if obj.geom else None
        coords = list(geom.exterior.coords) if geom else None
        data = {
            "id": obj.id,
            "name": obj.name,
            "geom": {"type": "Polygon", "coordinates": [coords]} if coords else None,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)