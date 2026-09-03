"""ONNX YOLOX detector adapter (Apache-2.0 licensed)."""
from typing import List
import numpy as np

from app.vision.types import Detector, DetectionCandidate, Frame
from app.vision.taxonomy import map_class


class OnnxDetector:
    """ONNX Runtime detector for YOLOX (or compatible models)."""

    def __init__(
        self,
        weights_path: str,
        providers: List[str] | None = None,
        input_size: tuple[int, int] = (640, 640),
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
    ):
        self.weights_path = weights_path
        self.input_size = input_size
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.detector_id = "yolox_onnx"
        self.model_version = "1.0.0"

        # Lazy import onnxruntime
        import onnxruntime as ort
        self.session = ort.InferenceSession(
            weights_path,
            providers=providers or ["CPUExecutionProvider"],
        )
        self.input_name = self.session.get_inputs()[0].name

    def detect(self, frame: Frame) -> List[DetectionCandidate]:
        """Run inference on frame."""
        import cv2

        # Preprocess
        img = self._preprocess(frame.image_bgr)
        outputs = self.session.run(None, {self.input_name: img})
        detections = self._postprocess(outputs[0], frame.image_bgr.shape[:2])
        return detections

    def _preprocess(self, image_bgr: np.ndarray) -> np.ndarray:
        import cv2
        h, w = image_bgr.shape[:2]
        scale = min(self.input_size[0] / h, self.input_size[1] / w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(image_bgr, (new_w, new_h))
        padded = np.full((self.input_size[0], self.input_size[1], 3), 114, dtype=np.uint8)
        padded[:new_h, :new_w] = resized
        # BGR to RGB, HWC to CHW, normalize
        padded = padded[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        return np.expand_dims(padded, 0)

    def _postprocess(
        self, output: np.ndarray, orig_shape: tuple[int, int]
    ) -> List[DetectionCandidate]:
        """Parse YOLOX output format: (batch, num_boxes, 5+num_classes)"""
        results = []
        h, w = orig_shape

        for det in output[0]:
            x1, y1, x2, y2, obj_conf = det[:5]
            class_scores = det[5:]
            class_id = int(np.argmax(class_scores))
            class_conf = float(class_scores[class_id])
            conf = float(obj_conf * class_conf)

            if conf < self.conf_threshold:
                continue

            class_name = map_class(class_id)
            if class_name is None:
                continue

            # Scale boxes back to original image
            x1 = float(x1 * w / self.input_size[1])
            y1 = float(y1 * h / self.input_size[0])
            x2 = float(x2 * w / self.input_size[1])
            y2 = float(y2 * h / self.input_size[0])

            results.append(DetectionCandidate(
                class_name=class_name,
                class_id=class_id,
                confidence=conf,
                bbox_xyxy=(x1, y1, x2, y2),
                detector_id=self.detector_id,
                model_version=self.model_version,
            ))

        return results