"""RTSP video source abstraction."""
import cv2
import re
from datetime import datetime
from uuid import UUID, uuid4
from urllib.parse import urlparse

from app.sources.base import VideoSource, Frame
from app.sources.types import VideoSourceMetadata
from app.core.errors import AppError, ErrorCode


class RTSPVideoSource:
    """Reads frames from an RTSP stream. MVP: basic retry."""

    def __init__(
        self,
        camera_id: UUID,
        rtsp_url: str,
        source_id: UUID | None = None,
        max_retries: int = 3,
    ):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.source_id = source_id or uuid4()
        self.max_retries = max_retries
        self._cap: cv2.VideoCapture | None = None
        self._fps: float = 0.0
        self._width: int = 0
        self._height: int = 0
        self._seq: int = 0

    def _redact_uri(self) -> str:
        """Redact credentials from RTSP URL for logging."""
        parsed = urlparse(self.rtsp_url)
        if parsed.password:
            redacted = parsed._replace(netloc=f"{parsed.username}:****@{parsed.hostname}")
            return redacted.geturl()
        return self.rtsp_url

    def open(self) -> None:
        for attempt in range(self.max_retries):
            self._cap = cv2.VideoCapture(self.rtsp_url)
            if self._cap.isOpened():
                self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
                self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self._seq = 0
                return
        raise AppError(ErrorCode.SERVICE_UNAVAILABLE, f"RTSP connection failed after {self.max_retries} retries")

    def read_frame(self) -> Frame | None:
        if self._cap is None:
            return None

        ret, frame = self._cap.read()
        if not ret:
            # Try reconnect once
            self._cap.release()
            self._cap = cv2.VideoCapture(self.rtsp_url)
            if not self._cap.isOpened():
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
            uri_redacted=self._redact_uri(),
            source_type="rtsp",
            width=self._width,
            height=self._height,
        )