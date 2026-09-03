"""IoU-based tracker (MVP fallback)."""
from typing import List
from datetime import datetime
from uuid import UUID

import numpy as np

from app.vision.tracker_base import Tracker, TrackUpdate
from app.vision.types import DetectionCandidate
from app.sources.base import Frame


def iou(box1, box2):
    """Compute IoU between two boxes in xyxy format."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0


class IoUTracker:
    """Greedy IoU matcher with class-aware matching."""

    def __init__(
        self,
        iou_threshold: float = 0.3,
        max_age: int = 30,
        min_hits: int = 3,
    ):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.min_hits = min_hits
        self.tracks = {}  # track_id -> track dict
        self.next_id = 1

    def update(
        self,
        frame: Frame,
        detections: List[DetectionCandidate],
    ) -> List[TrackUpdate]:
        now = frame.captured_at
        updates = []

        # Class-aware matching
        for det in detections:
            best_track = None
            best_iou = 0

            for tid, track in self.tracks.items():
                if track["class_name"] != det.class_name:
                    continue
                iou_val = iou(track["bbox"], det.bbox_xyxy)
                if iou_val > best_iou and iou_val >= self.iou_threshold:
                    best_iou = iou_val
                    best_track = tid

            if best_track is not None:
                # Update existing track
                track = self.tracks[best_track]
                track["bbox"] = det.bbox_xyxy
                track["centroid"] = (
                    (det.bbox_xyxy[0] + det.bbox_xyxy[2]) / 2,
                    (det.bbox_xyxy[1] + det.bbox_xyxy[3]) / 2,
                )
                track["last_seen"] = now
                track["confidence_sum"] += det.confidence
                track["hit_count"] += 1
                track["age"] = 0
            else:
                # Create new track
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = {
                    "bbox": det.bbox_xyxy,
                    "centroid": (
                        (det.bbox_xyxy[0] + det.bbox_xyxy[2]) / 2,
                        (det.bbox_xyxy[1] + det.bbox_xyxy[3]) / 2,
                    ),
                    "class_name": det.class_name,
                    "first_seen": now,
                    "last_seen": now,
                    "confidence_sum": det.confidence,
                    "hit_count": 1,
                    "age": 0,
                }

        # Age tracks and remove expired
        expired = []
        for tid, track in self.tracks.items():
            track["age"] += 1
            if track["age"] > self.max_age:
                expired.append(tid)
            elif track["hit_count"] >= self.min_hits:
                updates.append(TrackUpdate(
                    track_id=tid,
                    class_name=track["class_name"],
                    confidence=track["confidence_sum"] / track["hit_count"],
                    bbox_xyxy=track["bbox"],
                    centroid=track["centroid"],
                    first_seen=track["first_seen"],
                    last_seen=track["last_seen"],
                    camera_id=frame.camera_id,
                ))

        for tid in expired:
            del self.tracks[tid]

        return updates