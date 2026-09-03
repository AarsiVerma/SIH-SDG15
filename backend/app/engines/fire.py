"""Fire/smoke event mapping and severity heuristic."""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.models.enums import EventType
from app.engines.context import SceneContext


@dataclass
class FireAssessment:
    severity: str  # low|medium|high|critical
    nearby_ranger_ids: List[UUID]
    spread_prediction: Optional[dict]  # Always None in MVP


def assess_fire_event(event_type: EventType, confidence: float, ctx: SceneContext) -> FireAssessment:
    """Map fire/smoke detection to operational event."""
    if event_type == EventType.FIRE_DETECTED:
        if confidence >= 0.7:
            severity = "high"
        elif confidence >= 0.5:
            severity = "medium"
        else:
            severity = "low"
    else:  # smoke
        if confidence >= 0.7:
            severity = "medium"
        else:
            severity = "low"

    return FireAssessment(
        severity=severity,
        nearby_ranger_ids=ctx.nearby_ranger_ids,
        spread_prediction=None,  # MVP: no spread physics
    )