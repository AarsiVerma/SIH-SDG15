"""Vision types: DetectionCandidate and protocols."""
from dataclasses import dataclass
from typing import Protocol, List
from uuid import UUID

import numpy as np

from app.sources.base import Frame


@dataclass
class DetectionCandidate:
    """A single detection from a detector."""
    class_name: str  # person|vehicle|animal|fire|smoke|unknown
    class_id: int
    confidence: float  # 0-1
    bbox_xyxy: tuple[float, float, float, float]  # x1, y1, x2, y2
    detector_id: str
    model_version: str


class Detector(Protocol):
    """Detector protocol - implemented by DummyDetector, ONNXDetector, etc."""

    def detect(self, frame: Frame) -> List[DetectionCandidate]:
        """Run detection on a frame. Returns list of candidates."""
        ...