"""Correlation and duplicate suppression."""
import logging
from typing import List
from datetime import datetime

from app.engines.event_types import EventCandidate
from app.services.event_service import find_recent_by_correlation_key

logger = logging.getLogger("app.engines.correlation")


async def correlate(
    candidates: List[EventCandidate],
    session,
) -> List[EventCandidate]:
    """
    Merge candidates with same correlation_key within window.
    Update existing event if duplicate; otherwise return new.
    """
    merged = []
    seen_keys = set()

    for c in candidates:
        if c.correlation_key in seen_keys:
            continue

        # Check if recent event with same key exists
        existing = await find_recent_by_correlation_key(session, c.correlation_key, minutes=5)
        if existing:
            # Update existing event's payload/window
            existing.window_end = max(existing.window_end, c.window_end)
            existing.payload.update(c.payload)
            merged.append(existing)
            logger.debug("Merged event into existing correlation key: %s", c.correlation_key)
        else:
            merged.append(c)
            seen_keys.add(c.correlation_key)

    return merged