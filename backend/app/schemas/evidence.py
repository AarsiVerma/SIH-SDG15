"""Evidence schemas."""
from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EvidenceRead(BaseModel):
    id: UUID
    incident_id: UUID | None
    event_id: UUID | None
    camera_id: UUID
    kind: str
    storage_uri: str
    sha256: str
    captured_at: datetime
    bbox_xyxy: dict | None
    disclaimer_key: str

    model_config = ConfigDict(from_attributes=True)