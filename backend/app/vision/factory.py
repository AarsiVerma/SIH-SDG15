"""Detector and Tracker factories."""
from app.core.config import get_settings
from app.vision.dummy_detector import DummyDetector
from app.vision.bytetrack_tracker import ByteTrackTracker
from app.vision.iou_tracker import IoUTracker
from app.vision.types import Detector
from app.vision.tracker_base import Tracker


def build_detector(settings=None) -> Detector:
    """Build a detector based on configuration."""
    if settings is None:
        settings = get_settings()

    if settings.detector_backend == "onnx":
        from app.vision.onnx_detector import OnnxDetector
        weights_path = settings.models_dir / "yolox_s.onnx"
        if weights_path.exists():
            return OnnxDetector(str(weights_path))
        if settings.demo_mode:
            return DummyDetector()
        raise FileNotFoundError(f"ONNX weights not found at {weights_path}")

    return DummyDetector()


def build_tracker(settings=None) -> Tracker:
    """Build a tracker based on configuration."""
    if settings is None:
        settings = get_settings()

    if settings.tracker_backend == "bytetrack":
        return ByteTrackTracker()
    return IoUTracker()