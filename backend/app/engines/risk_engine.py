"""RiskEngine - deterministic scoring with explanations."""
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.engines.context import SceneContext
from app.engines.event_types import EventCandidate
from app.engines.risk_defaults import get_risk_weights
from app.models.enums import RiskLevel
from app.services.track_service import list_tracks
from app.db.session import get_session

logger = logging.getLogger("app.engines.risk")


@dataclass
class RiskFactorHit:
    code: str
    delta: int
    reason: str


@dataclass
class RiskAssessment:
    score: int
    level: RiskLevel
    factors: List[RiskFactorHit]
    requires_human_verification: bool


class RiskEngine:
    """Deterministic risk scoring with full explainability."""

    def __init__(self, weights: Dict[str, Any] | None = None):
        self.weights = weights or get_risk_weights()
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Validate weight configuration."""
        if "factors" not in self.weights:
            raise ValueError("Risk weights must contain 'factors'")
        if "levels" not in self.weights:
            raise ValueError("Risk weights must contain 'levels'")
        if "max_score" not in self.weights:
            raise ValueError("Risk weights must contain 'max_score'")

        for factor in self.weights["factors"]:
            if "code" not in factor or "delta" not in factor:
                raise ValueError(f"Invalid factor config: {factor}")

    async def score(
        self,
        event: EventCandidate,
        ctx: SceneContext,
        extra: Dict[str, Any] | None = None,
    ) -> RiskAssessment:
        """Score an event candidate with full factor breakdown."""
        factors = []
        score = 0

        # restricted_zone
        if ctx.in_restricted:
            factors.append(RiskFactorHit(
                code="restricted_zone",
                delta=self._factor_delta("restricted_zone"),
                reason="Activity occurred within a restricted zone",
            ))

        # nighttime
        if ctx.is_night:
            factors.append(RiskFactorHit(
                code="nighttime",
                delta=self._factor_delta("nighttime"),
                reason="Activity occurred during night hours",
            ))

        # vehicle - check track class names
        has_vehicle = any(
            "vehicle" in str(t).lower() for t in event.track_ids
        ) or any(
            c.get("class_name") == "vehicle" for c in event.payload.values() if isinstance(c, dict)
        ) or "vehicle" in str(event.payload.get("track_ids", []))
        if has_vehicle:
            factors.append(RiskFactorHit(
                code="vehicle",
                delta=self._factor_delta("vehicle"),
                reason="Vehicle detected in the scene",
            ))

        # suspicious_pattern (composite: person + vehicle + restricted + night)
        if ctx.in_restricted and ctx.is_night and len(event.track_ids) > 1:
            factors.append(RiskFactorHit(
                code="suspicious_pattern",
                delta=self._factor_delta("suspicious_pattern"),
                reason="Multiple actors in restricted zone at night",
            ))

        # wildlife_nearby
        if ctx.nearby_wildlife_track_ids:
            factors.append(RiskFactorHit(
                code="wildlife_nearby",
                delta=self._factor_delta("wildlife_nearby"),
                reason="Wildlife activity detected nearby",
            ))

        # repeated_movement: same camera person tracks >=3 in 30 min
        repeated = await self._check_repeated_movement(event.camera_id, event.window_end)
        if repeated:
            factors.append(RiskFactorHit(
                code="repeated_movement",
                delta=self._factor_delta("repeated_movement"),
                reason="Repeated person tracks in recent window",
            ))

        # authorized_ranger (negative delta)
        if ctx.nearby_ranger_ids:
            factors.append(RiskFactorHit(
                code="authorized_ranger",
                delta=self._factor_delta("authorized_ranger"),
                reason="Authorized ranger presence nearby",
            ))

        # Sum score
        for f in factors:
            score += f.delta

        # Clamp
        max_score = self.weights.get("max_score", 100)
        score = max(0, min(max_score, score))

        # Determine level
        level = self._score_to_level(score)

        return RiskAssessment(
            score=score,
            level=level,
            factors=factors,
            requires_human_verification=level in (RiskLevel.HIGH, RiskLevel.CRITICAL),
        )

    def _factor_delta(self, code: str) -> int:
        for f in self.weights.get("factors", []):
            if f["code"] == code:
                return f["delta"]
        logger.warning("Unknown risk factor code: %s", code)
        return 0

    def _score_to_level(self, score: int) -> RiskLevel:
        levels = self.weights.get("levels", {})
        if score >= levels.get("critical", [81, 100])[0]:
            return RiskLevel.CRITICAL
        elif score >= levels.get("high", [61, 80])[0]:
            return RiskLevel.HIGH
        elif score >= levels.get("medium", [31, 60])[0]:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    async def _check_repeated_movement(self, camera_id: UUID, at: datetime) -> bool:
        """Check for >=3 person tracks on same camera in last 30 min."""
        try:
            window_start = at - timedelta(minutes=30)
            async for session in get_session():
                tracks, _ = await list_tracks(
                    session,
                    camera_id=camera_id,
                    active_only=False,
                )
                person_tracks = [
                    t for t in tracks
                    if t.class_name == "person" and t.first_seen >= window_start
                ]
                return len(person_tracks) >= 3
        except Exception as e:
            logger.warning("Failed to check repeated movement: %s", e)
        return False