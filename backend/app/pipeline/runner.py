"""Pipeline runner: source -> sampler -> detect -> track -> persist."""
import asyncio
import logging
from uuid import UUID

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

logger = logging.getLogger("app.pipeline")


class PipelineRunner:
    """Runs an ingest job: open source, sample frames, detect, track, persist."""

    def __init__(
        self,
        job_id: UUID,
        target_fps: float = 2.0,
    ):
        self.job_id = job_id
        self.sampler = FrameSampler(target_fps)
        self.detector = build_detector(get_settings())
        self.tracker = build_tracker(get_settings())
        self._running = False

    async def run(self) -> None:
        """Execute the pipeline for the job."""
        self._running = True
        source = None
        frames_processed = 0
        detections_count = 0
        tracks_count = 0

        try:
            async for session in get_session():
                job = await session.get(IngestJob, self.job_id)
                if not job:
                    logger.error("Job %s not found", self.job_id)
                    return

                job.status = IngestJobStatus.RUNNING
                from datetime import datetime
                job.started_at = datetime.utcnow()
                await session.commit()

                # Get camera source
                source_stmt = select(CameraSource).where(CameraSource.camera_id == job.camera_id)
                source_row = (await session.execute(source_stmt)).scalar_one_or_none()
                if not source_row:
                    raise ValueError(f"No source for camera {job.camera_id}")

                source = build_source(source_row)
                source.open()

                await self._process_frames(source, job, session)

                job.status = IngestJobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.frames_processed = frames_processed
                job.detections_count = detections_count
                await session.commit()

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
        finally:
            if source:
                source.close()
            self._running = False

    async def _process_frames(
        self,
        source: VideoSource,
        job: IngestJob,
        session,
    ) -> None:
        frames_processed = 0
        detections_count = 0

        while self._running:
            frame = source.read_frame()
            if frame is None:
                break  # EOF

            if self.sampler.should_keep(frame):
                frames_processed += 1
                # Detect
                candidates = self.detector.detect(frame)
                if candidates:
                    created = await persist_detections(session, frame, candidates)
                    detections_count += len(created)

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
                        await append_track_points(session, track.id, [tu])

                # Update progress periodically
                if frames_processed % 100 == 0:
                    job.frames_processed = frames_processed
                    job.detections_count = detections_count
                    await session.commit()

        # Final update
        job.frames_processed = frames_processed
        job.detections_count = detections_count
        await session.commit()

    def stop(self) -> None:
        self._running = False