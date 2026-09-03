"""Tests for the event engine."""
import pytest
from datetime import datetime
from uuid import uuid4

from app.engines.event_engine import EventEngine
from app.engines.context import PostGISContextProvider, SceneContext
from app.vision.tracker_base import TrackUpdate
from app.models.enums import EventType
from app.core.config import get_settings


@pytest.fixture
def context_provider():
    """Create a context provider."""
    settings = get_settings()
    return PostGISContextProvider(settings)


@pytest.fixture
def event_engine(context_provider):
    """Create an event engine."""
    settings = get_settings()
    return EventEngine(context_provider, settings)


@pytest.fixture
def sample_context():
    """Create a sample scene context."""
    return SceneContext(
        camera_id=uuid4(),
        timestamp=datetime.utcnow(),
        zone_ids=[uuid4()],
        in_restricted=False,
        is_night=False,
        nearby_ranger_ids=[],
        nearby_wildlife_track_ids=[],
        camera_online=True,
    )


@pytest.fixture
def person_track():
    """Create a person track update."""
    return TrackUpdate(
        track_id=1,
        class_name="person",
        confidence=0.85,
        bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
        centroid=(150.0, 200.0),
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        camera_id=uuid4(),
    )


@pytest.fixture
def vehicle_track():
    """Create a vehicle track update."""
    return TrackUpdate(
        track_id=2,
        class_name="vehicle",
        confidence=0.90,
        bbox_xyxy=(300.0, 200.0, 500.0, 400.0),
        centroid=(400.0, 300.0),
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        camera_id=uuid4(),
    )


@pytest.fixture
def animal_track():
    """Create an animal track update."""
    return TrackUpdate(
        track_id=3,
        class_name="animal",
        confidence=0.75,
        bbox_xyxy=(150.0, 150.0, 250.0, 350.0),
        centroid=(200.0, 250.0),
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        camera_id=uuid4(),
    )


class TestEventEngine:
    """Test event generation from tracks and context."""

    def test_empty_tracks_returns_empty(self, event_engine):
        """Test empty track list returns no events."""
        events = event_engine.evaluate([], datetime.utcnow())
        assert events == []

    def test_person_in_restricted_zone(self, event_engine, person_track, sample_context):
        """Test person in restricted zone generates alertable event."""
        sample_context.in_restricted = True
        events = event_engine.evaluate([person_track], datetime.utcnow())
        
        restricted_events = [e for e in events if e.event_type == EventType.RESTRICTED_ZONE_ACTIVITY]
        assert len(restricted_events) == 1
        assert restricted_events[0].alertable is True

    def test_person_at_night(self, event_engine, person_track, sample_context):
        """Test person at night generates suspicious activity."""
        sample_context.is_night = True
        events = event_engine.evaluate([person_track], datetime.utcnow())
        
        suspicious = [e for e in events if e.event_type == EventType.SUSPICIOUS_ACTIVITY]
        assert len(suspicious) == 1
        assert suspicious[0].alertable is True

    def test_person_day_not_alertable(self, event_engine, person_track, sample_context):
        """Test person in non-restricted day not alertable."""
        sample_context.in_restricted = False
        sample_context.is_night = False
        events = event_engine.evaluate([person_track], datetime.utcnow())
        
        # PERSON_DETECTED should not be alertable
        person_events = [e for e in events if e.event_type == EventType.PERSON_DETECTED]
        assert len(person_events) == 1
        assert person_events[0].alertable is False

    def test_vehicle_in_restricted(self, event_engine, vehicle_track, sample_context):
        """Test vehicle in restricted zone generates alert."""
        sample_context.in_restricted = True
        events = event_engine.evaluate([vehicle_track], datetime.utcnow())
        
        restricted = [e for e in events if e.event_type == EventType.RESTRICTED_ZONE_ACTIVITY]
        assert len(restricted) == 1
        assert restricted[0].alertable is True

    def test_vehicle_not_restricted_not_alertable(self, event_engine, vehicle_track, sample_context):
        """Test vehicle outside restricted zone not alertable."""
        sample_context.in_restricted = False
        events = event_engine.evaluate([vehicle_track], datetime.utcnow())
        
        vehicle_events = [e for e in events if e.event_type == EventType.VEHICLE_DETECTED]
        assert len(vehicle_events) == 1
        assert vehicle_events[0].alertable is False

    def test_animal_never_alertable(self, event_engine, animal_track, sample_context):
        """Test animal detection never alertable by itself."""
        events = event_engine.evaluate([animal_track], datetime.utcnow())
        
        animal_events = [e for e in events if e.event_type == EventType.ANIMAL_DETECTED]
        assert len(animal_events) == 1
        assert animal_events[0].alertable is False

    def test_composite_suspicious_activity(self, event_engine, person_track, vehicle_track, sample_context):
        """Test person + vehicle + restricted + night = suspicious_activity_high_risk."""
        sample_context.in_restricted = True
        sample_context.is_night = True
        events = event_engine.evaluate([person_track, vehicle_track], datetime.utcnow())
        
        composite = [e for e in events if e.event_type == EventType.SUSPICIOUS_ACTIVITY_HIGH_RISK]
        assert len(composite) == 1
        assert composite[0].alertable is True
        assert composite[0].payload.get("person_count") == 1
        assert composite[0].payload.get("vehicle_count") == 1

    def test_fire_detection_alertable(self, event_engine, sample_context):
        """Test fire detection is alertable."""
        fire_track = TrackUpdate(
            track_id=4,
            class_name="fire",
            confidence=0.80,
            bbox_xyxy=(200.0, 200.0, 400.0, 400.0),
            centroid=(300.0, 300.0),
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            camera_id=uuid4(),
        )
        events = event_engine.evaluate([fire_track], datetime.utcnow())
        
        fire_events = [e for e in events if e.event_type == EventType.FIRE_DETECTED]
        assert len(fire_events) == 1
        assert fire_events[0].alertable is True

    def test_smoke_detection_alertable(self, event_engine, sample_context):
        """Test smoke detection is alertable."""
        smoke_track = TrackUpdate(
            track_id=5,
            class_name="smoke",
            confidence=0.70,
            bbox_xyxy=(200.0, 200.0, 400.0, 400.0),
            centroid=(300.0, 300.0),
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            camera_id=uuid4(),
        )
        events = event_engine.evaluate([smoke_track], datetime.utcnow())
        
        smoke_events = [e for e in events if e.event_type == EventType.SMOKE_DETECTED]
        assert len(smoke_events) == 1
        assert smoke_events[0].alertable is True

    def test_correlation_key_format(self, event_engine, person_track, sample_context):
        """Test correlation key follows expected format."""
        sample_context.in_restricted = True
        events = event_engine.evaluate([person_track], datetime.utcnow())
        
        for event in events:
            # Format: camera_id:family:bucket_epoch
            parts = event.correlation_key.split(":")
            assert len(parts) == 3
            assert str(event.camera_id) == parts[0]
            assert parts[1] in ("restricted", "suspicious", "person", "vehicle", "animal", "fire", "smoke")
            assert parts[2].isdigit()

    def test_event_has_required_fields(self, event_engine, person_track, sample_context):
        """Test all events have required fields."""
        events = event_engine.evaluate([person_track], datetime.utcnow())
        
        for event in events:
            assert event.event_type is not None
            assert event.language_key
            assert event.track_ids
            assert event.window_start
            assert event.window_end
            assert event.camera_id
            assert event.correlation_key
            assert event.geometry
            assert isinstance(event.alertable, bool)
            assert isinstance(event.payload, dict)