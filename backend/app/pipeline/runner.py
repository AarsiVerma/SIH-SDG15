"""Pipeline runner: source -> sampler -> detect -> track -> persist."""
import asyncio
import logging
import time
from uuid import UUID
from datetime import datetime
from typing import List

from app.sources.base import VideoSource, Frame
from app.pipeline.sampler import FrameSampler
from app.models import IngestJob, IngestJobStatus
from app.db.session import get_session
from app.sources.factory import build_source
from app.vision.factory import build_detector, build_tracker
from app.services.detection_service import persist_detections
from app.services.track_service import upsert_track, append_track_points
from app.models.camera import CameraSource
from sqlalchemy import select
from app.core.config import get_settings
from app.engines.context import PostGISContextProvider
from app.engines.event_engine import EventEngine
from app.engines.correlation import correlate
from app.engines.risk_engine import RiskEngine
from app.engines.incident_manager import IncidentManager
from app.services.event_service import upsert_event
from app.evidence.capture import capture_evidence_frame
from app.evidence.local_store import LocalEvidenceStore
from app.core.logging import (
    log_job_started, log_job_completed, log_job_failed,
    log_incident_created, log_evidence_created,
    log_detector_init, log_tracker_init,
)

logger = logging.getLogger("app.pipeline")


class PipelineRunner:
    """Runs an ingest job: open source, sample frames, detect, track, persist."""

    def __init__(
        self,
        job_id: UUID,
        target_fps: float = 2.0,
        db_batch_size: int = 50,
        commit_interval_seconds: float = 5.0,
    ):
        self.job_id = job_id
        self.sampler = FrameSampler(target_fps)
        self.detector = build_detector(get_settings())
        self.tracker = build_tracker(get_settings())
        self.db_batch_size = db_batch_size
        self.commit_interval_seconds = commit_interval_seconds
        self._running = False

        # Initialize engines for event processing
        settings = get_settings()
        self.context_provider = PostGISContextProvider(settings)
        self.event_engine = EventEngine(self.context_provider, settings)
        self.correlation_interval = 10  # Process events every N frames
        self.risk_engine = RiskEngine()
        self.incident_manager = IncidentManager(settings.incident_min_level)
        self.evidence_store = LocalEvidenceStore(settings.evidence_dir)

        # Log initialization
        log_detector_init(
            backend=type(self.detector).__name__,
            model_path=getattr(self.detector, 'weights_path', None),
        )
        log_tracker_init(
            backend=type(self.tracker).__name__,
            params={
                "track_thresh": getattr(self.tracker, 'track_thresh', None),
                "match_thresh": getattr(self.tracker, 'match_thresh', None),
            },
        )

    async def run(self) -> None:
        """Execute the pipeline for the job."""
        self._running = True
        source = None
        frames_processed = 0
        detections_count = 0
        tracks_count = 0
        events_count = 0
        incidents_count = 0
        last_commit_time = time.monotonic()
        pending_detections = []
        pending_track_points = []
        start_time = time.monotonic()

        try:
            async for session in get_session():
                job = await session.get(IngestJob, self.job_id)
                if not job:
                    logger.error("Job %s not found", self.job_id)
                    return

                job.status = IngestJobStatus.RUNNING
                job.started_at = datetime.utcnow()
                await session.commit()

                # Get camera source
                source_stmt = select(CameraSource).where(CameraSource.camera_id == job.camera_id)
                source_row = (await session.execute(source_stmt)).scalar_one_or_none()
                if not source_row:
                    raise ValueError(f"No source for camera {job.camera_id}")

                source = build_source(source_row)
                source.open()

                log_job_started(str(self.job_id), str(job.camera_id), self.sampler.target_fps)

                await self._process_frames(
                    source, job, session,
                    frames_processed, detections_count, tracks_count,
                    events_count, incidents_count,
                    last_commit_time, pending_detections, pending_track_points
                )

                job.status = IngestJobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.frames_processed = frames_processed
                job.detections_count = detections_count
                if hasattr(job, 'tracks_count'):
                    job.tracks_count = tracks_count
                if hasattr(job, 'events_count'):
                    job.events_count = events_count
                if hasattr(job, 'incidents_count'):
                    job.incidents_count = incidents_count
                await session.commit()

                duration_ms = (time.monotonic() - start_time) * 1000
                log_job_completed(str(self.job_id), str(job.camera_id), frames_processed, detections_count, duration_ms)

        except asyncio.CancelledError:
            logger.info("Pipeline cancelled for job %s", self.job_id)
            async for session in get_session():
                job = await session.get(IngestJob, self.job_id)
                if job:
                    job.status = IngestJobStatus.STOPPED
                    await session.commit()
            raise
        except Exception as e:
            logger.exception("Pipeline error for job %s: %s", self.job_id, e)
            async for session in get_session():
                job = await session.get(IngestJob, self.job_id)
                if job:
                    job.status = IngestJobStatus.FAILED
                    job.error = str(e)
                    await session.commit()
            log_job_failed(str(self.job_id), str(job.camera_id) if 'job' in locals() else "unknown", str(e))
        finally:
            if source:
                source.close()
            self._running = False

    async def _process_frames(
        self,
        source: VideoSource,
        job: IngestJob,
        session,
        frames_processed: int,
        detections_count: int,
        tracks_count: int,
        events_count: int,
        incidents_count: int,
        last_commit_time: float,
        pending_detections: List,
        pending_track_points: List,
    ) -> None:
        """Process frames with batched database commits."""
        # These are mutable integers that we'll update
        frame_count = frames_processed
        det_count = detections_count
        track_count = tracks_count
        event_count = events_count
        incident_count = incidents_count
        last_commit = last_commit_time

        while self._running:
            frame = source.read_frame()
            if frame is None:
                break  # EOF

            if self.sampler.should_keep(frame):
                frame_count += 1
                # Detect
                candidates = self.detector.detect(frame)
                if candidates:
                    # Persist detections (batched)
                    created = await persist_detections(session, frame, candidates)
                    det_count += len(created)
                    pending_detections.extend(created)

                    # Track
                    track_updates = self.tracker.update(frame, candidates)
                    for tu in track_updates:
                        track = await upsert_track(
                            session,
                            frame.camera_id,
                            tu.track_id,
                            tu.class_name,
                            tu.first_seen,
                            tu.last_seen,
                            tu.confidence,
                        )
                        track_count += 1 if track.created_at == track.updated_at else 0
                        await append_track_points(session, track.id, [tu])

                    # Process events periodically (every N frames)
                    if frame_count % self.correlation_interval == 0 and track_updates:
                        ctx = await self.context_provider.for_camera(frame.camera_id, frame.captured_at)
                        events = self.event_engine.evaluate(track_updates, frame.captured_at)

                        # Correlate events
                        merged_events = await correlate(events, session)

                        for ev in merged_events:
                            if ev.alertable:
                                risk = await self.risk_engine.score(ev, ctx)
                                await upsert_event(session, ev, risk.score, risk.level, [
                                    {"code": f.code, "delta": f.delta, "reason": f.reason}
                                    for f in risk.factors
                                ])
                                event_count += 1

                                # Create incident if risk is high enough
                                if risk.level.value >= self.incident_manager.incident_min_level.value:
                                    incident = await self.incident_manager.upsert_from_event(
                                        session, ev, risk.score, risk.level
                                    )
                                    if incident:
                                        incident_count += 1
                                        log_incident_created(
                                            str(incident.id),
                                            incident.public_id,
                                            incident.risk_level.value,
                                            str(frame.camera_id),
                                        )
                                        # Capture evidence for incident
                                        try:
                                            evidence_data = capture_evidence_frame(
                                                frame, track_updates, incident.id, self.evidence_store, session
                                            )
                                            log_evidence_created(
                                                evidence_data.sha256[:16],
                                                str(incident.id),
                                                evidence_data.sha256,
                                            )
                                            logger.debug("Captured evidence for incident %s: %s", incident.public_id, evidence_data.sha256)
                                        except Exception as e:
                                            logger.warning("Failed to capture evidence: %s", e)

                # Batch commit logic
                should_commit = (
                    frame_count % self.db_batch_size == 0 or
                    (time.monotonic() - last_commit) >= self.commit_interval_seconds
                )

                if should_commit:
                    job.frames_processed = frame_count
                    job.detections_count = det_count
                    if hasattr(job, 'tracks_count'):
                        job.tracks_count = track_count
                    if hasattr(job, 'events_count'):
                        job.events_count = event_count
                    if hasattr(job, 'incidents_count'):
                        job.incidents_count = incident_count
                    await session.commit()
                    last_commit = time.monotonic()
                    logger.debug(
                        "Job %s progress: frames=%d, detections=%d, tracks=%d, events=%d, incidents=%d",
                        self.job_id, frame_count, det_count, track_count, event_count, incident_count
                    )

        # Final commit
        job.frames_processed = frame_count
        job.detections_count = det_count
        if hasattr(job, 'tracks_count'):
            job.tracks_count = track_count
        if hasattr(job, 'events_count'):
            job.events_count = event_count
        if hasattr(job, 'incidents_count'):
            job.incidents_count = incident_count
        await session.commit()
        logger.info(
            "Job %s finished: frames=%d, detections=%d, tracks=%d, events=%d, incidents=%d",
            self.job_id, frame_count, det_count, track_count, event_count, incident_count
        )

    def stop(self) -> None:
        self._running = False