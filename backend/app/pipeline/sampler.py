"""Frame sampler for rate control."""
from app.sources.base import Frame


class FrameSampler:
    """Keeps frames at target FPS by elapsed time."""

    def __init__(self, target_fps: float):
        if target_fps <= 0:
            raise ValueError("target_fps must be positive")
        self.target_fps = target_fps
        self._interval = 1.0 / target_fps
        self._last_kept_ts: float | None = None

    def should_keep(self, frame: Frame) -> bool:
        """Return True if frame should be processed based on timestamp."""
        # Use frame timestamp (as float seconds since epoch)
        frame_ts = frame.captured_at.timestamp()

        if self._last_kept_ts is None:
            self._last_kept_ts = frame_ts
            return True

        if frame_ts - self._last_kept_ts >= self._interval:
            self._last_kept_ts = frame_ts
            return True

        return False

    def reset(self) -> None:
        self._last_kept_ts = None