"""Detection schemas and Taxonomy API."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DetectionRead(BaseModel):
    id: UUID
    camera_id: UUID
    frame_seq: int
    captured_at: datetime
    class_name: str
    class_id: int
    confidence: float
    bbox_xyxy: dict
    centroid: dict | None
    track_id: UUID | None
    detector_id: str
    model_version: str

    model_config = ConfigDict(from_attributes=True)


class TaxonomyClass(BaseModel):
    class_name: str
    class_id: int
    display_name: str
    language_key: Optional[str] = None
    layer: str = "detection"


TAXONOMY_CLASSES = [
    TaxonomyClass(class_name="person", class_id=0, display_name="Person", language_key="person_detected", layer="detection"),
    TaxonomyClass(class_name="vehicle", class_id=1, display_name="Vehicle", language_key="vehicle_detected", layer="detection"),
    TaxonomyClass(class_name="animal", class_id=2, display_name="Animal", language_key="animal_detected", layer="detection"),
    TaxonomyClass(class_name="fire", class_id=3, display_name="Possible Fire", language_key="fire_detected", layer="risk"),
    TaxonomyClass(class_name="smoke", class_id=4, display_name="Possible Smoke", language_key="smoke_detected", layer="detection"),
    TaxonomyClass(class_name="unknown", class_id=5, display_name="Unknown", language_key=None, layer="detection"),
]