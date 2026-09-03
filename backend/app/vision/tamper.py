"""Tamper/obstruction heuristics (MVP)."""
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class TamperResult:
    result: str  # none | obstruction_suspected | scene_change_suspected
    score: float
    reason: str


class TamperHeuristic:
    """MVP: brightness and frame difference checks."""

    def __init__(
        self,
        brightness_threshold: int = 10,
        brightness_duration: int = 30,  # frames
        scene_change_threshold: float = 0.95,  # MAD ratio
    ):
        self.brightness_threshold = brightness_threshold
        self.brightness_duration = brightness_duration
        self.scene_change_threshold = scene_change_threshold

        self.low_brightness_frames = 0
        self.reference_frame = None

    def check(self, frame: np.ndarray) -> TamperResult:
        """Run tamper checks on a frame."""
        gray = frame.mean() if frame.ndim == 3 else frame

        # Brightness check
        if gray < self.brightness_threshold:
            self.low_brightness_frames += 1
            if self.low_brightness_frames >= self.brightness_duration:
                return TamperResult(
                    result="obstruction_suspected",
                    score=1.0 - gray / 255.0,
                    reason="Sustained low brightness (possible obstruction)",
                )
        else:
            self.low_brightness_frames = 0

        # Scene change (MAD vs reference)
        if self.reference_frame is not None:
            mad = np.mean(np.abs(frame.astype(float) - self.reference_frame.astype(float)))
            ref_mad = np.mean(np.abs(self.reference_frame))
            if ref_mad > 0 and mad / ref_mad > self.scene_change_threshold:
                self.reference_frame = frame  # Update reference
                return TamperResult(
                    result="scene_change_suspected",
                    score=min(1.0, mad / ref_mad),
                    reason="Sudden large scene change detected",
                )
        else:
            self.reference_frame = frame

        return TamperResult(result="none", score=0.0, reason="")