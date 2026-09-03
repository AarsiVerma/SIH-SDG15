"""Tests for the risk engine."""
import pytest
from datetime import datetime
from uuid import uuid4

from app.engines.risk_engine import RiskEngine, RiskAssessment
from app.engines.context import SceneContext
from app.engines.event_types import EventCandidate
from app.models.enums import EventType, RiskLevel


@pytest.fixture
def risk_engine():
    """Create a risk engine with default weights."""
    return RiskEngine()


@pytest.fixture
def base_context():
    """Create a base scene context."""
    return SceneContext(
        camera_id=uuid4(),
        timestamp=datetime.utcnow(),
        zone_ids=[],
        in_restricted=False,
        is_night=False,
        nearby_ranger_ids=[],
        nearby_wildlife_track_ids=[],
        camera_online=True,
    )


@pytest.fixture
def base_event():
    """Create a base event candidate."""
    return EventCandidate(
        event_type=EventType.PERSON_DETECTED,
        language_key="person_detected",
        track_ids=[uuid4()],
        detection_ids=[],
        window_start=datetime.utcnow(),
        window_end=datetime.utcnow(),
        camera_id=uuid4(),
        correlation_key="test:person:123",
        geometry=(77.0, 12.0),
        alertable=False,
        payload={},
    )


class TestRiskEngine:
    """Test risk scoring functionality."""

    def test_zero_factors_returns_low(self, risk_engine, base_context, base_event):
        """Test that event with no risk factors returns LOW."""
        base_context.in_restricted = False
        base_context.is_night = False
        base_context.nearby_ranger_ids = []
        base_context.nearby_wildlife_track_ids = []
        base_event.track_ids = [uuid4()]

        risk = risk_engine.score(base_event, base_context)
        assert risk.level == RiskLevel.LOW
        assert risk.score == 0
        assert risk.requires_human_verification is False

    def test_restricted_zone_adds_score(self, risk_engine, base_context, base_event):
        """Test restricted zone factor."""
        base_context.in_restricted = True
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 25  # restricted_zone delta
        assert any(f.code == "restricted_zone" for f in risk.factors)

    def test_nighttime_adds_score(self, risk_engine, base_context, base_event):
        """Test nighttime factor."""
        base_context.is_night = True
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 10  # nighttime delta
        assert any(f.code == "nighttime" for f in risk.factors)

    def test_vehicle_adds_score(self, risk_engine, base_context, base_event):
        """Test vehicle detection factor."""
        base_event.payload = {"track_ids": ["vehicle_123"]}
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 15  # vehicle delta
        assert any(f.code == "vehicle" for f in risk.factors)

    def test_suspicious_pattern_composite(self, risk_engine, base_context, base_event):
        """Test suspicious pattern (person + vehicle + restricted + night)."""
        base_context.in_restricted = True
        base_context.is_night = True
        base_event.track_ids = [uuid4(), uuid4()]  # Multiple tracks
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 25  # suspicious_pattern delta
        assert any(f.code == "suspicious_pattern" for f in risk.factors)

    def test_wildlife_nearby_adds_score(self, risk_engine, base_context, base_event):
        """Test wildlife nearby factor."""
        base_context.nearby_wildlife_track_ids = [uuid4()]
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 15  # wildlife_nearby delta
        assert any(f.code == "wildlife_nearby" for f in risk.factors)

    def test_authorized_ranger_reduces_score(self, risk_engine, base_context, base_event):
        """Test authorized ranger negative factor."""
        base_context.nearby_ranger_ids = [uuid4()]
        base_context.in_restricted = True
        base_context.is_night = True
        risk = risk_engine.score(base_event, base_context)
        # Should have negative delta from ranger
        ranger_factor = next((f for f in risk.factors if f.code == "authorized_ranger"), None)
        assert ranger_factor is not None
        assert ranger_factor.delta < 0

    def test_score_clamped_to_max(self, risk_engine, base_context, base_event):
        """Test score is clamped to max_score."""
        # Add all positive factors
        base_context.in_restricted = True
        base_context.is_night = True
        base_event.payload = {"track_ids": ["vehicle_123"]}
        base_event.track_ids = [uuid4(), uuid4()]
        base_context.nearby_wildlife_track_ids = [uuid4()]
        
        risk = risk_engine.score(base_event, base_context)
        assert risk.score <= 100  # max_score

    def test_score_clamped_to_min(self, risk_engine, base_context, base_event):
        """Test score is clamped to 0 minimum."""
        # Add only negative factor (ranger) with no positive factors
        base_context.nearby_ranger_ids = [uuid4()]
        risk = risk_engine.score(base_event, base_context)
        assert risk.score >= 0

    def test_critical_threshold(self, risk_engine, base_context, base_event):
        """Test CRITICAL risk level threshold."""
        # Add enough factors to reach critical (81+)
        base_context.in_restricted = True  # +25
        base_context.is_night = True       # +10
        base_event.payload = {"track_ids": ["vehicle_123"]}  # +15
        base_event.track_ids = [uuid4(), uuid4()]  # +25 (suspicious_pattern)
        base_context.nearby_wildlife_track_ids = [uuid4()]  # +15
        # Total = 90 -> CRITICAL
        risk = risk_engine.score(base_event, base_context)
        assert risk.level == RiskLevel.CRITICAL
        assert risk.requires_human_verification is True

    def test_high_threshold(self, risk_engine, base_context, base_event):
        """Test HIGH risk level threshold."""
        base_context.in_restricted = True  # +25
        base_context.is_night = True       # +10
        base_event.payload = {"track_ids": ["vehicle_123"]}  # +15
        # Total = 50 -> MEDIUM
        # Add wildlife to reach HIGH (61+)
        base_context.nearby_wildlife_track_ids = [uuid4()]  # +15 = 65
        risk = risk_engine.score(base_event, base_context)
        assert risk.level == RiskLevel.HIGH
        assert risk.requires_human_verification is True

    def test_medium_threshold(self, risk_engine, base_context, base_event):
        """Test MEDIUM risk level threshold."""
        base_context.in_restricted = True  # +25
        base_context.is_night = True       # +10
        # Total = 35 -> MEDIUM
        risk = risk_engine.score(base_event, base_context)
        assert risk.level == RiskLevel.MEDIUM
        assert risk.requires_human_verification is False

    def test_same_input_produces_same_output(self, risk_engine, base_context, base_event):
        """Test deterministic scoring."""
        base_context.in_restricted = True
        base_context.is_night = True
        risk1 = risk_engine.score(base_event, base_context)
        risk2 = risk_engine.score(base_event, base_context)
        assert risk1.score == risk2.score
        assert risk1.level == risk2.level
        assert len(risk1.factors) == len(risk2.factors)

    def test_invalid_factor_code_returns_zero(self, risk_engine, base_context, base_event):
        """Test unknown factor code returns 0 delta."""
        # This tests internal _factor_delta method
        delta = risk_engine._factor_delta("nonexistent_factor")
        assert delta == 0

    def test_all_factors_explainable(self, risk_engine, base_context, base_event):
        """Test all factors have code, delta, and reason."""
        base_context.in_restricted = True
        base_context.is_night = True
        base_event.payload = {"track_ids": ["vehicle_123"]}
        base_event.track_ids = [uuid4(), uuid4()]
        base_context.nearby_wildlife_track_ids = [uuid4()]
        base_context.nearby_ranger_ids = [uuid4()]

        risk = risk_engine.score(base_event, base_context)
        for factor in risk.factors:
            assert factor.code
            assert factor.delta != 0
            assert factor.reason
            assert isinstance(factor.reason, str)