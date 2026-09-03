"""Tracker factory."""
from app.core.config import get_settings
from app.vision.iou_tracker import IoUTracker
from app.vision.bytetrack_tracker import ByteTrackTracker
from app.vision.tracker_base import Tracker


def build_tracker(settings=None) -> Tracker:
    """Build a tracker based on configuration."""
    if settings is None:
        settings = get_settings()

    if settings.tracker_backend == "bytetrack":
        return ByteTrackTracker()
    return IoUTracker()