"""Detector and Tracker factories."""
import logging
from pathlib import Path

from app.core.config import get_settings
from app.vision.dummy_detector import DummyDetector
from app.vision.bytetrack_tracker import ByteTrackTracker
from app.vision.iou_tracker import IoUTracker
from app.vision.types import Detector
from app.vision.tracker_base import Tracker

logger = logging.getLogger("app.vision.factory")


def build_detector(settings=None) -> Detector:
    """Build a detector based on configuration.
    
    Supported backends:
    - megadetector: MegaDetector v5 (PyTorch .pt) - recommended for demo
    - onnx: YOLOX ONNX (legacy)
    - dummy: Deterministic test detector
    
    In production mode, fails fast if weights are not found.
    In demo mode, falls back to DummyDetector for testing.
    """
    if settings is None:
        settings = get_settings()

    if settings.detector_backend == "megadetector":
        from app.vision.megadetector_detector import MegaDetector
        weights_path = settings.models_dir / "md_v5a.0.1.pt"
        if weights_path.exists():
            logger.info("Loading MegaDetector v5a from %s", weights_path)
            return MegaDetector(str(weights_path))
        if settings.demo_mode:
            logger.warning("MegaDetector weights not found at %s, falling back to DummyDetector (demo_mode=True)", weights_path)
            return DummyDetector()
        raise FileNotFoundError(
            f"MegaDetector weights not found at {weights_path}. "
            f"Set DETECTOR_BACKEND=dummy or place md_v5a.0.1.pt in {settings.models_dir}"
        )

    if settings.detector_backend == "onnx":
        from app.vision.onnx_detector import OnnxDetector
        weights_path = settings.models_dir / "yolox_s.onnx"
        if weights_path.exists():
            return OnnxDetector(str(weights_path))
        if settings.demo_mode:
            logger.warning("ONNX weights not found at %s, falling back to DummyDetector (demo_mode=True)", weights_path)
            return DummyDetector()
        raise FileNotFoundError(
            f"ONNX weights not found at {weights_path}. "
            f"Set DETECTOR_BACKEND=dummy or place yolox_s.onnx in {settings.models_dir}"
        )

    if settings.detector_backend == "dummy":
        return DummyDetector()

    raise ValueError(f"Unknown detector_backend: {settings.detector_backend}")


def build_tracker(settings=None) -> Tracker:
    """Build a tracker based on configuration."""
    if settings is None:
        settings = get_settings()

    if settings.tracker_backend == "bytetrack":
        return ByteTrackTracker()
    if settings.tracker_backend == "iou":
        return IoUTracker()
    raise ValueError(f"Unknown tracker_backend: {settings.tracker_backend}")