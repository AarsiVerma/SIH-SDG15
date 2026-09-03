"""ByteTrack tracker (MIT-licensed minimal implementation).

This is a minimal ByteTrack implementation. For production, vendor the full
ByteTrack from https://github.com/ifzhang/ByteTrack (MIT license).
"""
from typing import List
from datetime import datetime
from uuid import UUID

import numpy as np

from app.vision.tracker_base import Tracker, TrackUpdate
from app.vision.types import DetectionCandidate
from app.sources.base import Frame


def iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0


class KalmanFilter:
    """Simplified constant-velocity Kalman filter for 2D bbox."""
    def __init__(self):
        self.x = np.zeros((8, 1))  # [x, y, w, h, vx, vy, vw, vh]
        self.P = np.eye(8) * 10
        self.F = np.eye(8)
        self.F[0, 4] = self.F[1, 5] = self.F[2, 6] = self.F[3, 7] = 1.0
        self.Q = np.eye(8) * 0.01
        self.R = np.eye(4) * 0.1

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[:4].flatten()

    def update(self, z):
        y = z.reshape(-1, 1) - self.x[:4]
        S = self.P[:4, :4] + self.R
        K = self.P[:4, :4] @ np.linalg.inv(S)
        self.x[:4] += K @ y
        self.P = (np.eye(8) - np.vstack([np.hstack([K, np.zeros((4, 4))]), np.zeros((4, 8))])) @ self.P


class ByteTrackTracker:
    """ByteTrack with low/high confidence association."""

    def __init__(
        self,
        track_thresh: float = 0.5,
        match_thresh: float = 0.8,
        track_buffer: int = 30,
        min_box_area: int = 100,
    ):
        self.track_thresh = track_thresh
        self.match_thresh = match_thresh
        self.track_buffer = track_buffer
        self.min_box_area = min_box_area
        self.tracks = {}  # id -> dict
        self.next_id = 1

    def update(
        self,
        frame: Frame,
        detections: List[DetectionCandidate],
    ) -> List[TrackUpdate]:
        now = frame.captured_at
        updates = []

        # Separate high and low confidence
        high_conf = [d for d in detections if d.confidence >= self.track_thresh]
        low_conf = [d for d in detections if d.confidence < self.track_thresh]

        # Convert to boxes
        det_boxes = np.array([d.bbox_xyxy for d in high_conf])
        det_scores = np.array([d.confidence for d in high_conf])

        # Match high confidence with existing tracks
        track_ids = list(self.tracks.keys())
        if track_ids and len(det_boxes) > 0:
            track_boxes = np.array([self.tracks[tid]["kf"].predict() for tid in track_ids])
            iou_matrix = np.zeros((len(track_ids), len(det_boxes)))
            for i, tb in enumerate(track_boxes):
                for j, db in enumerate(det_boxes):
                    iou_matrix[i, j] = iou(tb, db)

            # Hungarian assignment (greedy for MVP)
            matched = []
            used_tracks = set()
            used_dets = set()
            for _ in range(min(len(track_ids), len(det_boxes))):
                i, j = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                if iou_matrix[i, j] < self.match_thresh:
                    break
                if i in used_tracks or j in used_dets:
                    iou_matrix[i, j] = 0
                    continue
                matched.append((i, j))
                used_tracks.add(i)
                used_dets.add(j)
                iou_matrix[i, j] = 0

            for i, j in matched:
                tid = track_ids[i]
                track = self.tracks[tid]
                det = high_conf[j]
                track["kf"].update(det_boxes[j])
                track["bbox"] = det.bbox_xyxy
                track["centroid"] = (
                    (det.bbox_xyxy[0] + det.bbox_xyxy[2]) / 2,
                    (det.bbox_xyxy[1] + det.bbox_xyxy[3]) / 2,
                )
                track["class_name"] = det.class_name
                track["last_seen"] = now
                track["age"] = 0
                track["hit_count"] += 1
                track["confidence_sum"] += det.confidence

        # Unmatched tracks age
        for tid in track_ids:
            if tid not in [m[0] for m in matched]:
                self.tracks[tid]["age"] += 1

        # New tracks from unmatched high-conf detections
        for j, det in enumerate(high_conf):
            if j in used_dets:
                continue
            tid = self.next_id
            self.next_id += 1
            self.tracks[tid] = {
                "kf": KalmanFilter(),
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
            # Initialize KF
            x1, y1, x2, y2 = det.bbox_xyxy
            self.tracks[tid]["kf"].x[:4] = np.array([[(x1+x2)/2], [(y1+y2)/2], [x2-x1], [y2-y1], [0], [0], [0], [0]])

        # Low confidence matching with unmatched tracks (simplified)
        # Omitted for MVP brevity

        # Build updates for confirmed tracks
        expired = []
        for tid, track in self.tracks.items():
            if track["hit_count"] >= 3:  # min_hits
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
            if track["age"] > self.track_buffer:
                expired.append(tid)

        for tid in expired:
            del self.tracks[tid]

        return updates