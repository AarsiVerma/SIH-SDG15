"""Inactivity/fall detection stub (FUTURE)."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class InactivityResult:
    active: bool
    reason: str


class InactivityMonitor:
    """Stub for future wearable-based inactivity/fall detection.

    MVP: always returns active=True with reason "not_implemented".
    Future: would check last location age, accelerometer data, etc.
    """

    def __init__(self, max_idle_seconds: int = 300):
        self.max_idle_seconds = max_idle_seconds

    def check(self, ranger_id: UUID) -> InactivityResult:
        """Check if ranger may be inactive/in distress."""
        return InactivityResult(active=True, reason="not_implemented")