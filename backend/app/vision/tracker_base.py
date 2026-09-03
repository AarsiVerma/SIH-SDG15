"""Tracker protocol and types."""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, List
from uuid import UUID


@dataclass
class TrackUpdate:
    """A track update from the tracker."""
    track_id: int
    class_name: str
    confidence: float
    bbox_xyxy: tuple[float, float, float, float]
    centroid: tuple[float, float]
    first_seen: datetime
    last_seen: datetime
    camera_id: UUID


class Tracker(Protocol):
    """Tracker protocol - implemented by IoUTracker, ByteTrackTracker."""

    def update(
        self,
        frame,
        detections: List["DetectionCandidate"],
    ) -> List[TrackUpdate]:
        """Update tracker with new frame and detections. Returns list of active tracks."""
        ...