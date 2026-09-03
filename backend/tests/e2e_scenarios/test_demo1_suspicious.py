import pytest

pytestmark = pytest.mark.postgres

"""E2E test for Demo 1: Suspicious Activity."""
from datetime import datetime
from uuid import uuid4

from datetime import datetime, timedelta
from app.sources.base import Frame
from app.vision.dummy_detector import DummyDetector
from app.vision.factory import build_tracker
from app.engines.context import PostGISContextProvider
from app.engines.event_engine import EventEngine
from app.engines.risk_engine import RiskEngine
from app.engines.incident_manager import IncidentManager
from app.services.detection_service import persist_detections
from app.services.track_service import upsert_track, append_track_points
from app.services.event_service import upsert_event
from app.db.session import get_session
from app.models import Camera
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_demo1_suspicious_activity(postgres_available):
    """Full pipeline: detect -> track -> context -> event -> risk -> incident."""
    if not postgres_available:
        pytest.skip("PostgreSQL with PostGIS not available")
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)
    event_engine = EventEngine(context_provider, settings)
    risk_engine = RiskEngine()
    incident_manager = IncidentManager(settings.incident_min_level)

    async with get_session() as session:
        # Get demo camera
        camera = await session.execute(
            Camera.__table__.select().where(Camera.code == "CAM-GATE-N")
        )
        camera = camera.scalar_one_or_none()
        if not camera:
            pytest.skip("Demo camera not seeded")

        # Simulate frames: person (10-20), vehicle (15-25) in restricted at night
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

            # Add detections per timeline
            candidates = []
            if 10 <= seq <= 20:
                candidates.append(detector._detect_from_script_single(frame, "person", 0.85, (100, 100, 200, 300)))
            if 15 <= seq <= 25:
                candidates.append(detector._detect_from_script_single(frame, "vehicle", 0.90, (300, 200, 500, 400)))

            if candidates:
                await persist_detections(session, frame, candidates)
                track_updates = tracker.update(frame, candidates)
                for tu in track_updates:
                    track = await upsert_track(session, frame.camera_id, tu.track_id, tu.class_name,
                                              tu.first_seen, tu.last_seen, tu.confidence)
                    await append_track_points(session, track.id, [tu])

        # Now evaluate events
        ctx = await context_provider.for_camera(camera.id, datetime(2026, 1, 1, 22, 0, 30))
        events = event_engine.evaluate(track_updates, datetime(2026, 1, 1, 22, 0, 30))

        # Should have suspicious_activity_high_risk
        suspicious = [e for e in events if e.event_type.value == "suspicious_activity_high_risk"]
        assert len(suspicious) == 1, f"Expected 1 suspicious event, got {len(suspicious)}"

        # Score risk
        risk = risk_engine.score(suspicious[0], ctx)
        assert risk.level.value in ("HIGH", "CRITICAL"), f"Risk level {risk.level} not HIGH/CRITICAL"
        assert risk.requires_human_verification is True

        # Create incident
        incident = await incident_manager.upsert_from_event(
            session, suspicious[0], risk.score, risk.level
        )
        assert incident is not None
        assert incident.risk_level in ("HIGH", "CRITICAL")
        assert incident.status.value == "NEW"

        await session.commit()
        print(f"Created incident {incident.public_id} with risk {incident.risk_level}")