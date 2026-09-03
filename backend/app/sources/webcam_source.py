"""Webcam video source."""
import cv2
from datetime import datetime
from uuid import UUID, uuid4

from app.sources.base import VideoSource, Frame
from app.sources.types import VideoSourceMetadata
from app.core.errors import AppError, ErrorCode


class WebcamUnavailable(AppError):
    def __init__(self, device_index: int):
        super().__init__(ErrorCode.WEBCAM_UNAVAILABLE, f"Webcam {device_index} unavailable")


class WebcamVideoSource:
    """Reads frames from a local webcam device."""

    def __init__(
        self,
        camera_id: UUID,
        device_index: int = 0,
        source_id: UUID | None = None,
    ):
        self.camera_id = camera_id
        self.device_index = device_index
        self.source_id = source_id or uuid4()
        self._cap: cv2.VideoCapture | None = None
        self._fps: float = 0.0
        self._width: int = 0
        self._height: int = 0
        self._seq: int = 0

    def open(self) -> None:
        self._cap = cv2.VideoCapture(self.device_index)
        if not self._cap.isOpened():
            raise WebcamUnavailable(self.device_index)

        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._seq = 0

    def read_frame(self) -> Frame | None:
        if self._cap is None:
            return None

        ret, frame = self._cap.read()
        if not ret:
            return None

        captured_at = datetime.utcnow()
        self._seq += 1

        return Frame(
            camera_id=self.camera_id,
            source_id=self.source_id,
            captured_at=captured_at,
            seq=self._seq,
            image_bgr=frame,
            width=self._width,
            height=self._height,
        )

    def close(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None

    def metadata(self) -> VideoSourceMetadata:
        return VideoSourceMetadata(
            fps_nominal=self._fps,
            uri_redacted=f"webcam:{self.device_index}",
            source_type="webcam",
            width=self._width,
            height=self._height,
        )