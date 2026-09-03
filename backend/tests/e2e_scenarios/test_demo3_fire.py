"""E2E test for Demo 3: Fire Detection."""
import pytest
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
async def test_demo3_fire_detection():
    """Fire detection creates HIGH incident."""
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)
    event_engine = EventEngine(context_provider, settings)
    risk_engine = RiskEngine()
    incident_manager = IncidentManager(settings.incident_min_level)

    async for session in get_session():
        camera = await session.execute(
            Camera.__table__.select().where(Camera.code == "CAM-WATCH-S")
        )
        camera = camera.scalar_one_or_none()
        if not camera:
            pytest.skip("Demo camera not seeded")

        for seq in range(1, 61):
            frame = Frame(
                camera_id=camera.id,
                source_id=None,
                captured_at=datetime(2026, 1, 1, 15, 0, 0) + timedelta(seconds=seq),
                seq=seq,
                image_bgr=None,
                width=640,
                height=480,
            )

            if 30 <= seq <= 50:
                candidates = [detector._detect_from_script_single(frame, "fire", 0.80, (200, 200, 400, 400))]
                await persist_detections(session, frame, candidates)
                track_updates = tracker.update(frame, candidates)
                for tu in track_updates:
                    track = await upsert_track(session, frame.camera_id, tu.track_id, tu.class_name,
                                              tu.first_seen, tu.last_seen, tu.confidence)
                    await append_track_points(session, track.id, [tu])

        ctx = await context_provider.for_camera(camera.id, datetime(2026, 1, 1, 15, 0, 40))
        events = event_engine.evaluate(track_updates, datetime(2026, 1, 1, 15, 0, 40))

        fire_events = [e for e in events if "fire" in e.language_key]
        assert len(fire_events) >= 1

        risk = risk_engine.score(fire_events[0], ctx)
        assert risk.level.value in ("HIGH", "CRITICAL")

        incident = await incident_manager.upsert_from_event(
            session, fire_events[0], risk.score, risk.level
        )
        assert incident is not None
        assert incident.risk_level in ("HIGH", "CRITICAL")
        assert incident.language_key == "fire_detected"

        await session.commit()
