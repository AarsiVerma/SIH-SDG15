"""MegaDetector v5 PyTorch detector wrapper."""
from typing import List
import numpy as np
import torch
import cv2

from app.vision.types import Detector, DetectionCandidate, Frame


class MegaDetector:
    """MegaDetector v5 wrapper for camera trap detection.
    
    Loads a TorchScript (.pt) model and runs inference on frames.
    Output classes: animal (1), person (2), vehicle (3).
    """

    # MegaDetector class mapping (from official release)
    CLASS_MAP = {
        1: "animal",
        2: "person",
        3: "vehicle",
        # 0 = blank/background (ignored)
    }

    def __init__(
        self,
        weights_path: str,
        conf_threshold: float = 0.2,
        device: str = "cpu",
    ):
        self.weights_path = weights_path
        self.conf_threshold = conf_threshold
        self.device = device
        self.detector_id = "megadetector_v5a"
        self.model_version = "5a"

        # Load model
        self.model = torch.jit.load(weights_path, map_location=device)
        self.model.eval().to(device)
        logger.info("MegaDetector loaded on %s", device)

    def detect(self, frame: Frame) -> List[DetectionCandidate]:
        """Run inference on a frame."""
        if frame.image_bgr is None:
            return []

        # Preprocess
        img_tensor = self._preprocess(frame.image_bgr)

        # Inference
        with torch.no_grad():
            predictions = self.model(img_tensor.to(self.device))

        # Postprocess
        detections = self._postprocess(predictions, frame.image_bgr.shape[:2])
        return detections

    def _preprocess(self, image_bgr: np.ndarray) -> torch.Tensor:
        """Resize, pad, normalize for MegaDetector (640x640)."""
        h, w = image_bgr.shape[:2]
        scale = min(640 / h, 640 / w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(image_bgr, (new_w, new_h))
        padded = np.full((640, 640, 3), 114, dtype=np.uint8)
        padded[:new_h, :new_w] = resized

        # BGR→RGB, HWC→CHW, normalize
        padded = padded[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        return torch.from_numpy(np.expand_dims(padded, 0))

    def _postprocess(self, predictions, orig_shape) -> List[DetectionCandidate]:
        """Parse YOLOv5-style output: [batch, num_boxes, 6] (x1, y1, x2, y2, conf, cls)."""
        h, w = orig_shape
        results = []

        # Handle different output formats
        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]

        # predictions shape: [1, num_boxes, 6] or [num_boxes, 6]
        if predictions.dim() == 3:
            predictions = predictions[0]

        for pred in predictions:
            x1, y1, x2, y2, conf, cls = pred[:6]
            conf = float(conf)
            if conf < self.conf_threshold:
                continue

            class_id = int(cls)
            class_name = self.CLASS_MAP.get(class_id)
            if not class_name:
                continue

            # Scale boxes back to original image
            x1 = float(x1 * w / 640)
            y1 = float(y1 * h / 640)
            x2 = float(x2 * w / 640)
            y2 = float(y2 * h / 640)

            results.append(DetectionCandidate(
                class_name=class_name,
                class_id=class_id,
                confidence=conf,
                bbox_xyxy=(x1, y1, x2, y2),
                detector_id=self.detector_id,
                model_version=self.model_version,
            ))

        return results


# Add logger import at top
import logging
logger = logging.getLogger("app.vision.megadetector")