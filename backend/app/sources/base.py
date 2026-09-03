"""VideoSource protocol and Frame contract."""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Optional
from uuid import UUID

import numpy as np


@dataclass
class Frame:
    """A single video frame with metadata."""
    camera_id: UUID
    source_id: UUID | None
    captured_at: datetime  # UTC
    seq: int
    image_bgr: np.ndarray  # HxWx3 uint8
    width: int
    height: int


class VideoSource(Protocol):
    """Hardware-agnostic video source interface."""

    def open(self) -> None:
        """Open the video source."""
        ...

    def read_frame(self) -> Frame | None:
        """Read next frame. Returns None at EOF or disconnect."""
        ...

    def close(self) -> None:
        """Close the video source."""
        ...

    def metadata(self) -> "VideoSourceMetadata":
        """Return source metadata."""
        ...