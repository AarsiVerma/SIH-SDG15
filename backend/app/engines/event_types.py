"""Event type catalog and EventCandidate."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models.enums import EventType, RiskLevel
from app.core.language import message_for


@dataclass
class EventCandidate:
    """An event candidate before correlation and risk scoring."""
    event_type: EventType
    language_key: str
    track_ids: List[UUID]
    detection_ids: List[UUID]
    window_start: datetime
    window_end: datetime
    camera_id: UUID
    correlation_key: str
    geometry: tuple[float, float]  # (lon, lat) from camera
    alertable: bool = False
    payload: dict = field(default_factory=dict)

    def title(self) -> str:
        return message_for(self.language_key)["title"]

    def body(self) -> str:
        return message_for(self.language_key)["body"]


def correlation_key(camera_id: UUID, event_family: str, bucket_epoch: int) -> str:
    """Generate correlation key: {camera_id}:{family}:{bucket_epoch}"""
    return f"{camera_id}:{event_family}:{bucket_epoch}"