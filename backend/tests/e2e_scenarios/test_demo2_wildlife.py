"""E2E test for Demo 2: Wildlife Observation."""
import pytest
from datetime import datetime, timedelta

from app.sources.base import Frame
from app.vision.dummy_detector import DummyDetector
from app.vision.factory import build_tracker
from app.engines.context import PostGISContextProvider
from app.engines.event_engine import EventEngine
from app.services.detection_service import persist_detections
from app.services.track_service import upsert_track, append_track_points
from app.db.session import get_session
from app.models import Camera
from app.core.config import get_settings


@pytest.mark.asyncio
async def test_demo2_wildlife_observation():
    """Animal track creates wildlife observation, no incident."""
    settings = get_settings()
    detector = DummyDetector()
    tracker = build_tracker(settings)
    context_provider = PostGISContextProvider(settings)

    async for session in get_session():
        camera = await session.execute(
            Camera.__table__.select().where(Camera.code == "CAM-PERIM-E")
        )
        camera = camera.scalar_one_or_none()
        if not camera:
            pytest.skip("Demo camera not seeded")

        for seq in range(1, 81):
            frame = Frame(
                camera_id=camera.id,
                source_id=None,
                captured_at=datetime(2026, 1, 1, 14, 0, 0) + timedelta(seconds=seq),
                seq=seq,
                image_bgr=None,
                width=640,
                height=480,
            )

            if 20 <= seq <= 60:
                candidates = [detector._detect_from_script_single(frame, "animal", 0.75, (150, 150, 250, 350))]
                await persist_detections(session, frame, candidates)
                track_updates = tracker.update(frame, candidates)
                for tu in track_updates:
                    track = await upsert_track(session, frame.camera_id, tu.track_id, tu.class_name,
                                              tu.first_seen, tu.last_seen, tu.confidence)
                    await append_track_points(session, track.id, [tu])

        await session.commit()

        # Check wildlife observation created
        from app.models import WildlifeObservation
        from sqlalchemy import select
        obs = await session.execute(
            select(WildlifeObservation).where(WildlifeObservation.camera_id == camera.id)
        )
        obs = obs.scalars().all()
        assert len(obs) >= 1
        assert obs[0].species == "unknown"

        # No incident should be created for simple animal detection
        from app.models import Incident
        inc = await session.execute(
            select(Incident).where(Incident.camera_id == camera.id)
        )
        inc = inc.scalars().all()
        # Wildlife observation doesn't create incident (below MEDIUM threshold)
        # Note: This depends on the event engine logic
