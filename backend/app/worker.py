"""Worker process for video ingestion jobs."""
import asyncio
import logging
import signal
import sys
from uuid import UUID

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import get_session, engine
from app.models import IngestJob, IngestJobStatus
from app.pipeline.runner import PipelineRunner
from sqlalchemy import select, update

configure_logging()
logger = logging.getLogger("app.worker")
settings = get_settings()


class Worker:
    """Background worker that processes video ingestion jobs."""

    def __init__(self, poll_interval: float = 5.0, max_concurrent: int = 1):
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self._running = False
        self._tasks: set[asyncio.Task] = set()

    async def start(self) -> None:
        """Start the worker."""
        self._running = True
        logger.info("Worker started (poll_interval=%.1fs, max_concurrent=%d)", self.poll_interval, self.max_concurrent)

        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._shutdown)

        while self._running:
            try:
                await self._process_pending_jobs()
            except Exception as e:
                logger.exception("Error in worker main loop: %s", e)
            await asyncio.sleep(self.poll_interval)

        # Wait for running tasks to complete
        if self._tasks:
            logger.info("Waiting for %d running jobs to complete...", len(self._tasks))
            await asyncio.gather(*self._tasks, return_exceptions=True)

        logger.info("Worker stopped")

    def _shutdown(self) -> None:
        """Signal handler for graceful shutdown."""
        logger.info("Shutdown signal received")
        self._running = False

    async def _process_pending_jobs(self) -> None:
        """Find and process pending ingestion jobs."""
        async for session in get_session():
            # Find jobs that are QUEUED or stuck in RUNNING (stale)
            stmt = select(IngestJob).where(
                IngestJob.status.in_([IngestJobStatus.QUEUED, IngestJobStatus.RUNNING])
            ).order_by(IngestJob.created_at).limit(self.max_concurrent)

            # Use FOR UPDATE SKIP LOCKED to safely claim jobs
            stmt = stmt.with_for_update(skip_locked=True)
            result = await session.execute(stmt)
            jobs = result.scalars().all()

            for job in jobs:
                if job.status == IngestJobStatus.RUNNING:
                    # Check if job is stale (no update for 5 minutes)
                    from datetime import datetime, timedelta
                    if job.updated_at and (datetime.utcnow() - job.updated_at) > timedelta(minutes=5):
                        logger.warning("Recovering stale job %s", job.id)
                    else:
                        continue  # Still actively running

                # Claim the job
                job.status = IngestJobStatus.RUNNING
                job.started_at = datetime.utcnow()
                await session.commit()
                logger.info("Claimed job %s for camera %s", job.id, job.camera_id)

                # Start processing in background
                task = asyncio.create_task(self._run_job(job.id))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)

    async def _run_job(self, job_id: UUID) -> None:
        """Run a single ingestion job."""
        runner = PipelineRunner(job_id)
        try:
            await runner.run()
            logger.info("Job %s completed successfully", job_id)
        except asyncio.CancelledError:
            logger.info("Job %s cancelled", job_id)
            raise
        except Exception as e:
            logger.exception("Job %s failed: %s", job_id, e)
            # Error handling is done in runner


async def main() -> None:
    worker = Worker(
        poll_interval=settings.offline_after_seconds if hasattr(settings, 'offline_after_seconds') else 5.0,
        max_concurrent=1,  # MVP: single concurrent job
    )
    await worker.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass