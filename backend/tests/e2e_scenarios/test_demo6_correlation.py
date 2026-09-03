import pytest
pytestmark = pytest.mark.postgres

"""E2E test for Demo 6: Correlation (one incident, not five)."""
from datetime import datetime, timedelta

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
from app.models import Camera
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_demo6_correlation_single_incident():
    """Person + vehicle + restricted + night → ONE incident."""
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)
    event_engine = EventEngine(context_provider, settings)
    risk_engine = RiskEngine()
    incident_manager = IncidentManager(settings.incident_min_level)

    async for session in get_session():
        camera = await session.execute(
            Camera.__table__.select().where(Camera.code == "CAM-GATE-N")
        )
        camera = camera.scalar_one_or_none()
        if not camera:
            pytest.skip("Demo camera not seeded")

        for seq in range(1, 31):
            frame = Frame(
                camera_id=camera.id,
                source_id=None,
                captured_at=datetime(2026, 1, 1, 22, 0, 0) + timedelta(seconds=seq),
                seq=seq,
                image_bgr=None,
                width=640,
                height=480,
            )

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

        ctx = await context_provider.for_camera(camera.id, datetime(2026, 1, 1, 22, 0, 30))
        events = event_engine.evaluate(track_updates, datetime(2026, 1, 1, 22, 0, 30))

        # Correlate
        merged = await correlate(events, session)

        # Should have ONE alertable event (suspicious_activity_high_risk)
        alertable = [e for e in merged if e.alertable]
        assert len(alertable) == 1
        assert alertable[0].event_type.value == "suspicious_activity_high_risk"

        # Create incident
        risk = risk_engine.score(alertable[0], ctx)
        incident = await incident_manager.upsert_from_event(
            session, alertable[0], risk.score, risk.level
        )

        # Verify only ONE incident created
        from app.models import Incident
        from sqlalchemy import select
        incidents = await session.execute(
            select(Incident).where(Incident.camera_id == camera.id)
        )
        incidents = incidents.scalars().all()
        assert len(incidents) == 1

        await session.commit()
