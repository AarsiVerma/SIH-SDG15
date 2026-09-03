"""Camera management API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.camera import CameraCreate, CameraRead, CameraUpdate, CameraSourceCreate, CameraSourceRead
from app.schemas.common import Page
from app.services.camera_service import (
    list_cameras, get_camera, create_camera, update_camera, delete_camera, add_camera_source,
)

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=Page[CameraRead])
async def list_cameras_endpoint(
    pagination: Pagination,
    forest_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_cameras(db, pagination.limit, pagination.offset, forest_id, status)
    # Convert ORM to schema manually
    from app.schemas.camera import CameraRead
    camera_reads = [CameraRead.from_orm(c) for c in items]
    return Page(items=camera_reads, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
async def create_camera_endpoint(
    data: CameraCreate,
    db: AsyncSession = Depends(get_db),
):
    camera = await create_camera(db, data)
    return CameraRead.from_orm(camera)


@router.get("/{camera_id}", response_model=CameraRead)
async def get_camera_endpoint(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    camera = await get_camera(db, camera_id)
    if not camera:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Camera not found")
    return CameraRead.from_orm(camera)


@router.patch("/{camera_id}", response_model=CameraRead)
async def update_camera_endpoint(
    camera_id: UUID,
    data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
):
    camera = await update_camera(db, camera_id, data)
    if not camera:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Camera not found")
    return CameraRead.from_orm(camera)


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera_endpoint(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_camera(db, camera_id)
    if not deleted:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Camera not found")


@router.post("/{camera_id}/sources", response_model=CameraSourceRead, status_code=status.HTTP_201_CREATED)
async def add_camera_source_endpoint(
    camera_id: UUID,
    data: CameraSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    source = await add_camera_source(db, camera_id, data)
    if not source:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Camera not found")
    return source