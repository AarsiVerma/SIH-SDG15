"""GeoJSON schemas."""
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, ConfigDict


class Geometry(BaseModel):
    type: str  # Point, Polygon, etc.
    coordinates: List[Union[List[float], float]]  # varies by type

    model_config = ConfigDict(from_attributes=True)


class Feature(BaseModel):
    type: str = "Feature"
    geometry: Optional[Geometry] = None
    properties: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Feature]

    model_config = ConfigDict(from_attributes=True)