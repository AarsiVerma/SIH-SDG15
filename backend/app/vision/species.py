"""Species classifier protocol and null implementation."""
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

import numpy as np


@dataclass
class SpeciesResult:
    label: str
    confidence: float
    unverified: bool = True


class SpeciesClassifier(Protocol):
    def classify(self, crop_bgr: np.ndarray) -> SpeciesResult: ...


class NullSpeciesClassifier:
    """Default: always returns unknown."""

    def classify(self, crop_bgr: np.ndarray) -> SpeciesResult:
        return SpeciesResult(label="unknown", confidence=0.0, unverified=True)


class MegaDetectorAdapter:
    """Optional MegaDetector adapter (requires weights and license review)."""

    def __init__(self, weights_path: str, threshold: float = 0.5):
        self.weights_path = weights_path
        self.threshold = threshold
        # Lazy load onnxruntime and model

    def classify(self, crop_bgr: np.ndarray) -> SpeciesResult:
        raise NotImplementedError("MegaDetector not implemented in MVP. Enable with species_backend=megadetector and valid weights.")