"""File-based video source (MP4 simulation)."""
import cv2
from pathlib import Path
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.sources.base import VideoSource, Frame
from app.sources.types import VideoSourceMetadata
from app.core.errors import AppError, ErrorCode


class FileVideoSource:
    """Reads frames from an MP4 file. Simulates capture timestamps."""

    def __init__(
        self,
        camera_id: UUID,
        path: Path | str,
        *,
        loop: bool = False,
        source_id: UUID | None = None,
        start_time: datetime | None = None,
    ):
        self.camera_id = camera_id
        self.path = Path(path)
        self.loop = loop
        self.source_id = source_id or uuid4()
        self.start_time = start_time or datetime.utcnow()
        self._cap: cv2.VideoCapture | None = None
        self._fps: float = 0.0
        self._width: int = 0
        self._height: int = 0
        self._seq: int = 0

    def open(self) -> None:
        if not self.path.exists():
            raise AppError(ErrorCode.NOT_FOUND, f"Video file not found: {self.path}")

        self._cap = cv2.VideoCapture(str(self.path))
        if not self._cap.isOpened():
            raise AppError(ErrorCode.SERVICE_UNAVAILABLE, f"Could not open video: {self.path}")

        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._seq = 0

    def read_frame(self) -> Frame | None:
        if self._cap is None:
            return None

        ret, frame = self._cap.read()
        if not ret:
            if self.loop:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._cap.read()
                if not ret:
                    return None
            else:
                return None

        # Simulate timestamp: start_time + seq/fps
        captured_at = self.start_time + timedelta(seconds=self._seq / self._fps)
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
            uri_redacted=str(self.path),
            source_type="file",
            width=self._width,
            height=self._height,
        )