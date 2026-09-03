"""Ingest job control API."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.models import IngestJob, IngestJobStatus
from app.schemas.common import Page
from app.services.ingest_service import (
    create_ingest_job, get_ingest_job, list_ingest_jobs, update_job_status,
)

router = APIRouter(prefix="/ingest", tags=["ingest"])


class JobCreateRequest(BaseModel):
    camera_id: UUID


class JobControlRequest(BaseModel):
    pass  # empty for stop


class JobRead(BaseModel):
    id: UUID
    camera_id: UUID
    status: IngestJobStatus
    frames_processed: int
    detections_count: int
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("/jobs", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    data: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    job = await create_ingest_job(db, data.camera_id)
    return job


@router.get("/jobs", response_model=Page[JobRead])
async def list_jobs_endpoint(
    pagination: Pagination,
    camera_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_ingest_jobs(db, pagination.limit, pagination.offset, camera_id, status)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job_endpoint(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    job = await get_ingest_job(db, job_id)
    if not job:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Job not found")
    return job


@router.post("/jobs/{job_id}/stop", response_model=JobRead)
async def stop_job_endpoint(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    job = await update_job_status(db, job_id, IngestJobStatus.STOPPED)
    if not job:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Job not found")
    return job