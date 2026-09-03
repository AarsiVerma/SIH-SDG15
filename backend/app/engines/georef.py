"""Homography-optional object map point (MVP stub)."""
from typing import Optional
from uuid import UUID

from app.models import Camera


def estimate_map_point(camera: Camera, bbox: tuple[float, float, float, float]) -> Optional[tuple[float, float]]:
    """
    Estimate map point (lon, lat) for a detection bbox.

    MVP: returns None. Future: use camera calibration (homography) from camera.extra_json.
    """
    # Camera calibration not available in MVP
    # Camera point is used for zone membership instead
    return None