"""Risk weights and preview API."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.engines.risk_engine import RiskEngine
from app.engines.risk_defaults import get_risk_weights, get_incident_min_level
from app.engines.event_types import EventCandidate
from app.engines.context import PostGISContextProvider
from app.core.config import get_settings

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/weights")
async def get_weights():
    return get_risk_weights()


@router.get("/min-incident-level")
async def get_min_level():
    return {"level": get_incident_min_level()}


@router.post("/preview")
async def preview_risk(
    # Simplified: accept event flags for preview
    restricted: bool = False,
    night: bool = False,
    vehicle: bool = False,
    repeated: bool = False,
    wildlife: bool = False,
    ranger_nearby: bool = False,
):
    """Dry-run risk scoring with given flags."""
    engine = RiskEngine()

    # Build mock candidate and context
    from datetime import datetime
    from uuid import uuid4

    candidate = EventCandidate(
        event_type="suspicious_activity",
        language_key="suspicious_activity",
        track_ids=[uuid4()],
        detection_ids=[],
        window_start=datetime.utcnow(),
        window_end=datetime.utcnow(),
        camera_id=uuid4(),
        correlation_key="preview",
        geometry=(0, 0),
        alertable=True,
        payload={
            "track_ids": [1, 2] if vehicle else [1],
        },
    )

    from app.engines.context import SceneContext
    ctx = SceneContext(
        camera_id=uuid4(),
        timestamp=datetime.utcnow(),
        zone_ids=[],
        in_restricted=restricted,
        is_night=night,
        nearby_ranger_ids=[uuid4()] if ranger_nearby else [],
        nearby_wildlife_track_ids=[uuid4()] if wildlife else [],
        camera_online=True,
    )

    assessment = engine.score(candidate, ctx)
    return {
        "score": assessment.score,
        "level": assessment.level.value,
        "factors": [
            {"code": f.code, "delta": f.delta, "reason": f.reason}
            for f in assessment.factors
        ],
        "requires_human_verification": assessment.requires_human_verification,
    }