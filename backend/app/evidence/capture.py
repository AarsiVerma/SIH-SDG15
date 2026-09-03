"""Capture annotated frames for evidence."""
import cv2
import numpy as np
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.sources.base import Frame
from app.vision.tracker_base import TrackUpdate
from app.models import Event, Incident, EvidenceKind
from app.evidence.local_store import LocalEvidenceStore
from app.services.evidence_service import create_evidence
from app.core.language import message_for


@dataclass
class EvidenceRef:
    """Reference to captured evidence."""
    sha256: str
    storage_uri: str
    nbytes: int


def annotate_frame(frame: Frame, tracks: list[TrackUpdate]) -> np.ndarray:
    """Draw bounding boxes and labels on frame."""
    if frame.image_bgr is None:
        # Create a blank frame if no image
        img = np.zeros((frame.height, frame.width, 3), dtype=np.uint8)
    else:
        img = frame.image_bgr.copy()
    for t in tracks:
        x1, y1, x2, y2 = map(int, t.bbox_xyxy)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{t.class_name} {t.confidence:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return img


async def capture_evidence_frame(
    frame: Frame,
    tracks: list[TrackUpdate],
    incident_id: UUID,
    store: LocalEvidenceStore,
    db: AsyncSession,
) -> EvidenceRef:
    """Save annotated frame as evidence linked to incident."""
    if not tracks:
        raise ValueError("No tracks to capture")

    # Annotate
    annotated = annotate_frame(frame, tracks)

    # Encode JPEG
    _, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
    data = buffer.tobytes()

    # Store
    ref = store.put_bytes(data, suffix=".jpg")

    # Disclaimer from catalog
    disclaimer_key = "evidence"

    # Persist
    await create_evidence(
        db=db,
        incident_id=incident_id,
        event_id=None,  # Will be linked via incident
        camera_id=frame.camera_id,
        kind=EvidenceKind.FRAME,
        storage_uri=ref.storage_uri,
        sha256=ref.sha256,
        captured_at=frame.captured_at,
        bbox_xyxy={
            "x1": min(t.bbox_xyxy[0] for t in tracks),
            "y1": min(t.bbox_xyxy[1] for t in tracks),
            "x2": max(t.bbox_xyxy[2] for t in tracks),
            "y2": max(t.bbox_xyxy[3] for t in tracks),
        },
        disclaimer_key=disclaimer_key,
    )

    return ref