#!/usr/bin/env python3
"""Demo scripts for the seven SIH scenarios."""

import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

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


class DemoScript:
    """Base demo script runner."""

    def __init__(self):
        self.settings = get_settings()
        self.detector = DummyDetector()
        self.tracker = build_tracker(self.settings)
        self.context_provider = PostGISContextProvider(self.settings)
        self.event_engine = EventEngine(self.context_provider, self.settings)
        self.risk_engine = RiskEngine()
        self.incident_manager = IncidentManager(self.settings.incident_min_level)

    async def run_scenario(self, camera_code: str, frames: int, timeline: dict):
        """
        timeline: {frame_seq: [("person", conf, bbox), ("vehicle", conf, bbox), ...]}
        """
        async for session in get_session():
            camera = await session.execute(
                Camera.__table__.select().where(Camera.code == camera_code)
            )
            camera = camera.scalar_one_or_none()
            if not camera:
                raise ValueError(f"Camera {camera_code} not found")

            for seq in range(1, frames + 1):
                frame = Frame(
                    camera_id=camera.id,
                    source_id=None,
                    captured_at=datetime.utcnow() + timedelta(seconds=seq),
                    seq=seq,
                    image_bgr=None,  # DummyDetector doesn't need image
                    width=640,
                    height=480,
                )

                # Run detector
                candidates = self.detector.detect(frame)

                # Override with timeline if provided
                if seq in timeline:
                    candidates = []
                    for class_name, conf, bbox in timeline[seq]:
                        candidates.append(self.detector._detect_from_script_single(
                            frame, class_name, conf, bbox
                        ))

                if candidates:
                    await persist_detections(session, frame, candidates)

                    # Track
                    track_updates = self.tracker.update(frame, candidates)
                    for tu in track_updates:
                        track = await upsert_track(
                            session, frame.camera_id, tu.track_id, tu.class_name,
                            tu.first_seen, tu.last_seen, tu.confidence
                        )
                        await append_track_points(session, track.id, [tu])

                # Event engine every 10 frames
                if seq % 10 == 0 and track_updates:
                    ctx = await self.context_provider.for_camera(camera.id, frame.captured_at)
                    events = self.event_engine.evaluate(track_updates, frame.captured_at)

                    for ev in events:
                        risk = self.risk_engine.score(ev, ctx)
                        await upsert_event(session, ev, risk.score, risk.level, [
                            {"code": f.code, "delta": f.delta, "reason": f.reason}
                            for f in risk.factors
                        ])

                        # Incident manager
                        if ev.alertable and risk.level.value >= "medium":
                            await self.incident_manager.upsert_from_event(
                                session, ev, risk.score, risk.level
                            )

            await session.commit()
            print(f"Scenario complete for {camera_code}")


# Add helper to DummyDetector
def _detect_from_script_single(self, frame, class_name, conf, bbox):
    from app.vision.types import DetectionCandidate
    from app.vision.dummy_detector import DummyDetector
    class_id = DummyDetector.TAXONOMY.get(class_name, 5)
    return DetectionCandidate(
        class_name=class_name,
        class_id=class_id,
        confidence=conf,
        bbox_xyxy=bbox,
        detector_id=self.detector_id,
        model_version=self.model_version,
    )

DummyDetector._detect_from_script_single = _detect_from_script_single


async def demo_suspicious():
    """Demo 1: Person + vehicle in restricted zone at night."""
    print("=== DEMO 1: Suspicious Activity ===")
    script = DemoScript()
    # Night + restricted + person + vehicle
    timeline = {
        10: [("person", 0.85, (100, 100, 200, 300))],
        15: [("vehicle", 0.90, (300, 200, 500, 400))],
    }
    await script.run_scenario("CAM-GATE-N", 50, timeline)


async def demo_wildlife():
    """Demo 2: Animal in corridor."""
    print("=== DEMO 2: Wildlife Observation ===")
    script = DemoScript()
    timeline = {i: [("animal", 0.75, (150, 150, 250, 350))] for i in range(20, 60)}
    await script.run_scenario("CAM-PERIM-E", 80, timeline)


async def demo_fire():
    """Demo 3: Fire detection."""
    print("=== DEMO 3: Fire Detection ===")
    script = DemoScript()
    timeline = {i: [("fire", 0.80, (200, 200, 400, 400))] for i in range(30, 50)}
    await script.run_scenario("CAM-WATCH-S", 60, timeline)


async def demo_camera_fail():
    """Demo 4: Camera failure (handled by health service, not here)."""
    print("=== DEMO 4: Camera Failure ===")
    print("Stop worker container, wait 35s, check /api/v1/cameras/health")


async def demo_sos():
    """Demo 5: Ranger SOS."""
    print("=== DEMO 5: Ranger SOS ===")
    print("POST /api/v1/sos/rangers/<id>/sos")


async def demo_correlation():
    """Demo 6: One incident, not five."""
    print("=== DEMO 6: Correlation ===")
    script = DemoScript()
    timeline = {
        10: [("person", 0.85, (100, 100, 200, 300))],
        12: [("vehicle", 0.90, (300, 200, 500, 400))],
        15: [("person", 0.80, (110, 105, 210, 310))],
    }
    await script.run_scenario("CAM-GATE-N", 60, timeline)
    print("Verify only ONE incident created")


async def demo_offline():
    """Demo 7: Offline sync."""
    print("=== DEMO 7: Offline Sync ===")
    print("Run scripts/demo_offline_sync.py")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m app.demo.scripts <demo_name>")
        print("Demos: suspicious, wildlife, fire, camera_fail, sos, correlation, offline")
        sys.exit(1)

    demo_map = {
        "suspicious": demo_suspicious,
        "wildlife": demo_wildlife,
        "fire": demo_fire,
        "camera_fail": demo_camera_fail,
        "sos": demo_sos,
        "correlation": demo_correlation,
        "offline": demo_offline,
    }
    if sys.argv[1] in demo_map:
        asyncio.run(demo_map[sys.argv[1]]())
    else:
        print(f"Unknown demo: {sys.argv[1]}")