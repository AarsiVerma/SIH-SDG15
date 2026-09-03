"""Full end-to-end integration test for the complete pipeline."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.sources.base import Frame
from app.vision.dummy_detector import DummyDetector
from app.vision.factory import build_tracker
from app.engines.context import PostGISContextProvider
from app.engines.event_engine import EventEngine
from app.engines.correlation import correlate
from app.engines.risk_engine import RiskEngine
from app.engines.incident_manager import IncidentManager
from app.services.detection_service import persist_detections
from app.services.track_service import upsert_track, append_track_points
from app.services.event_service import upsert_event
from app.db.session import get_session
from app.models import Camera, IngestJob, IngestJobStatus
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_full_pipeline_suspicious_activity(db_session):
    """
    Complete pipeline test:
    Video -> Detect -> Track -> Context -> Event -> Correlate -> Risk -> Incident -> Evidence
    """
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)
    event_engine = EventEngine(context_provider, settings)
    risk_engine = RiskEngine()
    incident_manager = IncidentManager(settings.incident_min_level)

    # Get demo camera
    camera = await db_session.execute(
        Camera.__table__.select().where(Camera.code == "CAM-GATE-N")
    )
    camera = camera.scalar_one_or_none()
    if not camera:
        pytest.skip("Demo camera not seeded - run seed_demo.py first")

    # Simulate frames: person (10-20), vehicle (15-25) in restricted at night
    track_updates = []
    for seq in range(1, 31):
        frame = Frame(
            camera_id=camera.id,
            source_id=None,
            captured_at=datetime(2026, 1, 1, 22, 0, 0) + timedelta(seconds=seq),  # 22:00 = night
            seq=seq,
            image_bgr=None,
            width=640,
            height=480,
        )

        candidates = []
        if 10 <= seq <= 20:
            candidates.append(detector._detect_from_script_single(
                frame, "person", 0.85, (100, 100, 200, 300)
            ))
        if 15 <= seq <= 25:
            candidates.append(detector._detect_from_script_single(
                frame, "vehicle", 0.90, (300, 200, 500, 400)
            ))

        if candidates:
            await persist_detections(db_session, frame, candidates)
            track_updates = tracker.update(frame, candidates)
            for tu in track_updates:
                track = await upsert_track(
                    db_session, frame.camera_id, tu.track_id, tu.class_name,
                    tu.first_seen, tu.last_seen, tu.confidence
                )
                await append_track_points(db_session, track.id, [tu])

    # Verify detections and tracks were created
    from app.models import Detection, Track
    detections = await db_session.execute(
        Detection.__table__.select().where(Detection.camera_id == camera.id)
    )
    detections = detections.scalars().all()
    assert len(detections) > 0

    tracks = await db_session.execute(
        Track.__table__.select().where(Track.camera_id == camera.id)
    )
    tracks = tracks.scalars().all()
    assert len(tracks) > 0

    # Now evaluate events
    ctx = await context_provider.for_camera(camera.id, datetime(2026, 1, 1, 22, 0, 30))
    events = event_engine.evaluate(track_updates, datetime(2026, 1, 1, 22, 0, 30))

    # Should have suspicious_activity_high_risk
    suspicious = [e for e in events if e.event_type.value == "suspicious_activity_high_risk"]
    assert len(suspicious) == 1, f"Expected 1 suspicious event, got {len(suspicious)}"

    # Correlate
    merged = await correlate(events, db_session)
    alertable = [e for e in merged if e.alertable]
    assert len(alertable) == 1

    # Score risk
    risk = risk_engine.score(alertable[0], ctx)
    assert risk.level.value in ("HIGH", "CRITICAL"), f"Risk level {risk.level} not HIGH/CRITICAL"
    assert risk.requires_human_verification is True

    # Create incident
    incident = await incident_manager.upsert_from_event(
        db_session, alertable[0], risk.score, risk.level
    )
    assert incident is not None
    assert incident.risk_level in ("HIGH", "CRITICAL")
    assert incident.status.value == "NEW"

    # Verify incident has events linked
    from app.models import IncidentEvent, IncidentStatusHistory
    incident_events = await db_session.execute(
        IncidentEvent.__table__.select().where(IncidentEvent.incident_id == incident.id)
    )
    incident_events = incident_events.scalars().all()
    assert len(incident_events) >= 1

    # Verify status history
    history = await db_session.execute(
        IncidentStatusHistory.__table__.select().where(IncidentStatusHistory.incident_id == incident.id)
    )
    history = history.scalars().all()
    assert len(history) == 1
    assert history[0].to_status == "NEW"

    # Verify evidence would be created (if capture function called)
    # This is tested separately in evidence tests

    await db_session.commit()
    print(f"Full pipeline test passed: Created incident {incident.public_id} with risk {incident.risk_level}")


@pytest.mark.asyncio
async def test_pipeline_wildlife_no_incident(db_session):
    """Test wildlife observation doesn't create incident."""
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)
    event_engine = EventEngine(context_provider, settings)
    risk_engine = RiskEngine()
    incident_manager = IncidentManager(settings.incident_min_level)

    camera = await db_session.execute(
        Camera.__table__.select().where(Camera.code == "CAM-PERIM-E")
    )
    camera = camera.scalar_one_or_none()
    if not camera:
        pytest.skip("Demo camera not seeded")

    track_updates = []
    for seq in range(1, 61):
        frame = Frame(
            camera_id=camera.id,
            source_id=None,
            captured_at=datetime(2026, 1, 1, 14, 0, 0) + timedelta(seconds=seq),  # 14:00 = day
            seq=seq,
            image_bgr=None,
            width=640,
            height=480,
        )

        candidates = []
        if 20 <= seq <= 60:
            candidates.append(detector._detect_from_script_single(
                frame, "animal", 0.75, (150, 150, 250, 350)
            ))

        if candidates:
            await persist_detections(db_session, frame, candidates)
            track_updates = tracker.update(frame, candidates)
            for tu in track_updates:
                track = await upsert_track(
                    db_session, frame.camera_id, tu.track_id, tu.class_name,
                    tu.first_seen, tu.last_seen, tu.confidence
                )
                await append_track_points(db_session, track.id, [tu])

    ctx = await context_provider.for_camera(camera.id, datetime(2026, 1, 1, 14, 0, 30))
    events = event_engine.evaluate(track_updates, datetime(2026, 1, 1, 14, 0, 30))

    # Should have animal event but not alertable
    animal_events = [e for e in events if e.event_type.value == "animal_detected"]
    assert len(animal_events) == 1
    assert animal_events[0].alertable is False

    # Correlate and score
    merged = await correlate(events, db_session)
    alertable = [e for e in merged if e.alertable]
    assert len(alertable) == 0  # No alertable events

    # No incident should be created
    for e in merged:
        risk = risk_engine.score(e, ctx)
        incident = await incident_manager.upsert_from_event(
            db_session, e, risk.score, risk.level
        )
        assert incident is None

    await db_session.commit()
    print("Wildlife test passed: No incident created for animal observation")