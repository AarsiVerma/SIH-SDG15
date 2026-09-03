"""Tests for the incident manager."""
import pytest
from datetime import datetime
from uuid import uuid4

from app.engines.incident_manager import IncidentManager
from app.engines.event_types import EventCandidate
from app.engines.risk_engine import RiskEngine
from app.engines.context import SceneContext
from app.models.enums import EventType, RiskLevel, IncidentStatus
from app.models import Incident


@pytest.fixture
def incident_manager():
    """Create an incident manager."""
    return IncidentManager(incident_min_level="medium")


@pytest.fixture
def risk_engine():
    """Create a risk engine."""
    return RiskEngine()


@pytest.fixture
def sample_context():
    """Create a sample scene context."""
    return SceneContext(
        camera_id=uuid4(),
        timestamp=datetime.utcnow(),
        zone_ids=[],
        in_restricted=True,
        is_night=True,
        nearby_ranger_ids=[],
        nearby_wildlife_track_ids=[],
        camera_online=True,
    )


@pytest.fixture
def high_risk_event():
    """Create a high-risk event candidate."""
    return EventCandidate(
        event_type=EventType.SUSPICIOUS_ACTIVITY_HIGH_RISK,
        language_key="suspicious_activity_high_risk",
        track_ids=[uuid4(), uuid4()],
        detection_ids=[],
        window_start=datetime.utcnow(),
        window_end=datetime.utcnow(),
        camera_id=uuid4(),
        correlation_key=f"{uuid4()}:suspicious_high:123",
        geometry=(77.0, 12.0),
        alertable=True,
        payload={"night": True, "restricted": True, "person_count": 1, "vehicle_count": 1},
    )


class TestIncidentManager:
    """Test incident management functionality."""

    @pytest.mark.asyncio
    async def test_create_new_incident(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test creating a new incident from high-risk event."""
        risk = risk_engine.score(high_risk_event, sample_context)
        incident = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        
        assert incident is not None
        assert incident.status == IncidentStatus.NEW
        assert incident.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
        assert incident.public_id.startswith("INC-")
        assert incident.location is not None

    @pytest.mark.asyncio
    async def test_no_incident_below_threshold(self, incident_manager, risk_engine, sample_context, db_session):
        """Test no incident created for low-risk event."""
        low_risk_event = EventCandidate(
            event_type=EventType.PERSON_DETECTED,
            language_key="person_detected",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=uuid4(),
            correlation_key=f"{uuid4()}:person:123",
            geometry=(77.0, 12.0),
            alertable=False,
            payload={},
        )
        # Make it low risk
        sample_context.in_restricted = False
        sample_context.is_night = False
        
        risk = risk_engine.score(low_risk_event, sample_context)
        incident = await incident_manager.upsert_from_event(
            db_session, low_risk_event, risk.score, risk.level
        )
        
        assert incident is None

    @pytest.mark.asyncio
    async def test_duplicate_event_same_incident(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test duplicate event links to existing incident."""
        risk = risk_engine.score(high_risk_event, sample_context)
        
        # Create first incident
        incident1 = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        await db_session.commit()
        
        # Try to create again with same event
        incident2 = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        
        assert incident2 is not None
        assert incident2.id == incident1.id

    @pytest.mark.asyncio
    async def test_correlation_merge(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test events with same correlation family merge into one incident."""
        risk = risk_engine.score(high_risk_event, sample_context)
        
        # Create first incident
        incident1 = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        await db_session.commit()
        
        # Create second event with same correlation family but different key
        event2 = EventCandidate(
            event_type=EventType.RESTRICTED_ZONE_ACTIVITY,
            language_key="restricted_zone_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=high_risk_event.camera_id,
            correlation_key=f"{high_risk_event.camera_id}:restricted:123",
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"night": True, "track_id": str(uuid4())},
        )
        
        risk2 = risk_engine.score(event2, sample_context)
        incident2 = await incident_manager.upsert_from_event(
            db_session, event2, risk2.score, risk2.level
        )
        
        # Should merge into same incident
        assert incident2 is not None
        assert incident2.id == incident1.id

    @pytest.mark.asyncio
    async def test_incident_status_history(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test incident status history is recorded."""
        risk = risk_engine.score(high_risk_event, sample_context)
        incident = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        
        from app.services.incident_service import get_incident_history
        history = await get_incident_history(db_session, incident.id)
        
        assert len(history) == 1
        assert history[0].to_status == IncidentStatus.NEW
        assert history[0].from_status is None

    @pytest.mark.asyncio
    async def test_public_id_format(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test public ID follows expected format."""
        risk = risk_engine.score(high_risk_event, sample_context)
        incident = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        
        # Format: INC-YYYY-NNNN
        import re
        assert re.match(r"INC-\d{4}-\d{4}", incident.public_id)

    @pytest.mark.asyncio
    async def test_risk_score_updates_on_merge(self, incident_manager, risk_engine, sample_context, high_risk_event, db_session):
        """Test incident risk score updates when merging higher risk event."""
        risk = risk_engine.score(high_risk_event, sample_context)
        incident1 = await incident_manager.upsert_from_event(
            db_session, high_risk_event, risk.score, risk.level
        )
        original_score = incident1.risk_score
        await db_session.commit()
        
        # Create higher risk event
        higher_risk_event = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY_HIGH_RISK,
            language_key="suspicious_activity_high_risk",
            track_ids=[uuid4(), uuid4(), uuid4()],  # More tracks
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=high_risk_event.camera_id,
            correlation_key=f"{high_risk_event.camera_id}:suspicious_high:124",  # Different bucket
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"night": True, "restricted": True, "person_count": 2, "vehicle_count": 1},
        )
        
        risk2 = risk_engine.score(higher_risk_event, sample_context)
        incident2 = await incident_manager.upsert_from_event(
            db_session, higher_risk_event, risk2.score, risk2.level
        )
        
        assert incident2.risk_score >= original_score