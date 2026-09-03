"""Simple wildlife movement anomaly detection."""
from typing import Optional
from uuid import UUID

from app.models import TrackPoint
from app.db.session import get_session


def is_anomalous(track_id: UUID) -> tuple[bool, Optional[str]]:
    """
    Heuristic anomaly detection for wildlife tracks.
    Returns (is_anomalous, reason_code).
    """
    async for session in get_session():
        # Get track points ordered by time
        stmt = select(TrackPoint).where(
            TrackPoint.track_id == track_id
        ).order_by(TrackPoint.captured_at)
        # Note: would need actual session execution here
        # For MVP, simplified logic
        pass

    # Placeholder logic - in production would query track points
    # and compute: speed, track length, revisit frequency
    return False, None


# Reason codes for event engine
ANOMALY_REASONS = {
    "high_speed": "Unusually fast movement detected",
    "long_duration": "Extended presence in area",
    "revisit": "Repeated returns to same location",
}