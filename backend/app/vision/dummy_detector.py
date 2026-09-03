"""DummyDetector - deterministic detections for tests and GPU-less demos."""
from typing import List, Optional
from uuid import UUID

import numpy as np

from app.vision.types import Detector, DetectionCandidate, Frame


class DummyDetector:
    """Deterministic detector driven by frame sequence or a script.

    Script format: list of (start_seq, end_seq, class_name, confidence, bbox)
    """

    TAXONOMY = {
        "person": 0,
        "vehicle": 1,
        "animal": 2,
        "fire": 3,
        "smoke": 4,
        "unknown": 5,
    }

    def __init__(
        self,
        detector_id: str = "dummy",
        model_version: str = "0.1.0",
        script: Optional[list] = None,
    ):
        self.detector_id = detector_id
        self.model_version = model_version
        self.script = script or []

    def detect(self, frame: Frame) -> List[DetectionCandidate]:
        """Return detections based on script or default pattern."""
        if self.script:
            return self._detect_from_script(frame)
        return self._detect_default(frame)

    def _detect_from_script(self, frame: Frame) -> List[DetectionCandidate]:
        results = []
        for entry in self.script:
            start, end, class_name, conf, bbox = entry
            if start <= frame.seq <= end:
                class_id = self.TAXONOMY.get(class_name, 5)
                results.append(DetectionCandidate(
                    class_name=class_name,
                    class_id=class_id,
                    confidence=conf,
                    bbox_xyxy=bbox,
                    detector_id=self.detector_id,
                    model_version=self.model_version,
                ))
        return results

    def _detect_default(self, frame: Frame) -> List[DetectionCandidate]:
        """Default: person in frames 10-50, vehicle in 60-80."""
        results = []
        if 10 <= frame.seq <= 50:
            results.append(DetectionCandidate(
                class_name="person",
                class_id=0,
                confidence=0.85,
                bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
                detector_id=self.detector_id,
                model_version=self.model_version,
            ))
        if 60 <= frame.seq <= 80:
            results.append(DetectionCandidate(
                class_name="vehicle",
                class_id=1,
                confidence=0.90,
                bbox_xyxy=(300.0, 200.0, 500.0, 400.0),
                detector_id=self.detector_id,
                model_version=self.model_version,
            ))
        return results