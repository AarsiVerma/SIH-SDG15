"""Ingest job service."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IngestJob, IngestJobStatus, Camera
from app.core.errors import AppError, ErrorCode


async def create_ingest_job(db: AsyncSession, camera_id: UUID) -> IngestJob:
    camera = await db.execute(select(Camera).where(Camera.id == camera_id))
    if not camera.scalar_one_or_none():
        raise AppError(ErrorCode.NOT_FOUND, "Camera not found")

    job = IngestJob(camera_id=camera_id, status=IngestJobStatus.QUEUED)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_ingest_job(db: AsyncSession, job_id: UUID) -> IngestJob | None:
    stmt = select(IngestJob).where(IngestJob.id == job_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_ingest_jobs(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    camera_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> tuple[list[IngestJob], int]:
    stmt = select(IngestJob)
    if camera_id:
        stmt = stmt.where(IngestJob.camera_id == camera_id)
    if status:
        stmt = stmt.where(IngestJob.status == status)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(IngestJob.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def update_job_status(
    db: AsyncSession,
    job_id: UUID,
    status: IngestJobStatus,
    **kwargs,
) -> IngestJob | None:
    job = await get_ingest_job(db, job_id)
    if not job:
        return None
    job.status = status
    for k, v in kwargs.items():
        setattr(job, k, v)
    await db.commit()
    await db.refresh(job)
    return job