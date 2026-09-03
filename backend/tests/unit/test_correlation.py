import pytest
pytestmark = pytest.mark.postgres

"""Tests for the correlation engine."""
from datetime import datetime
from uuid import uuid4

from app.engines.correlation import correlate
from app.engines.event_types import EventCandidate
from app.models.enums import EventType


class TestCorrelation:
    """Test event correlation functionality."""

    @pytest.mark.asyncio
    async def test_same_key_merged(self, db_session):
        """Test events with same correlation key are merged."""
        camera_id = uuid4()
        key = f"{camera_id}:suspicious:123"
        
        event1 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"track_id": str(uuid4())},
        )
        
        event2 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"track_id": str(uuid4())},
        )
        
        merged = await correlate([event1, event2], db_session)
        assert len(merged) == 1

    @pytest.mark.asyncio
    async def test_different_keys_not_merged(self, db_session):
        """Test events with different correlation keys are not merged."""
        camera_id = uuid4()
        
        event1 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=f"{camera_id}:suspicious:123",
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        event2 = EventCandidate(
            event_type=EventType.RESTRICTED_ZONE_ACTIVITY,
            language_key="restricted_zone_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=f"{camera_id}:restricted:123",
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        merged = await correlate([event1, event2], db_session)
        assert len(merged) == 2

    @pytest.mark.asyncio
    async def test_existing_db_event_merged(self, db_session):
        """Test candidate merges with existing database event."""
        camera_id = uuid4()
        key = f"{camera_id}:suspicious:123"
        
        # First, create an event in the database
        from app.services.event_service import upsert_event
        existing_event = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"original": True},
        )
        await upsert_event(db_session, existing_event)
        await db_session.commit()
        
        # Now correlate with new candidate with same key
        new_candidate = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={"new": True},
        )
        
        merged = await correlate([new_candidate], db_session)
        assert len(merged) == 1
        # Payload should be merged
        assert "original" in merged[0].payload
        assert "new" in merged[0].payload

    @pytest.mark.asyncio
    async def test_window_end_updated(self, db_session):
        """Test window_end is updated to max of both events."""
        camera_id = uuid4()
        key = f"{camera_id}:suspicious:123"
        early = datetime.utcnow()
        late = early.replace(second=early.second + 30)
        
        event1 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=early,
            window_end=early,
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        event2 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=late,
            window_end=late,
            camera_id=camera_id,
            correlation_key=key,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        merged = await correlate([event1, event2], db_session)
        assert merged[0].window_end == late

    @pytest.mark.asyncio
    async def test_different_cameras_not_merged(self, db_session):
        """Test events from different cameras don't merge even with same family/bucket."""
        cam1 = uuid4()
        cam2 = uuid4()
        key1 = f"{cam1}:suspicious:123"
        key2 = f"{cam2}:suspicious:123"
        
        event1 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=cam1,
            correlation_key=key1,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        event2 = EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            language_key="suspicious_activity",
            track_ids=[uuid4()],
            detection_ids=[],
            window_start=datetime.utcnow(),
            window_end=datetime.utcnow(),
            camera_id=cam2,
            correlation_key=key2,
            geometry=(77.0, 12.0),
            alertable=True,
            payload={},
        )
        
        merged = await correlate([event1, event2], db_session)
        assert len(merged) == 2