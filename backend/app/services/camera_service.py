"""Camera service."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from geoalchemy2 import WKTElement

from app.models.camera import Camera, CameraSource
from app.schemas.camera import CameraCreate, CameraUpdate, CameraSourceCreate
from app.core.errors import AppError, ErrorCode


async def list_cameras(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    forest_id: Optional[UUID] = None,
    status: Optional[str] = None,
) -> tuple[list[Camera], int]:
    stmt = select(Camera).options(selectinload(Camera.sources))
    if forest_id:
        stmt = stmt.where(Camera.forest_id == forest_id)
    if status:
        stmt = stmt.where(Camera.status == status)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Camera.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_camera(db: AsyncSession, camera_id: UUID) -> Camera | None:
    stmt = select(Camera).options(selectinload(Camera.sources)).where(Camera.id == camera_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_camera(db: AsyncSession, data: CameraCreate) -> Camera:
    # Check code uniqueness
    existing = await db.execute(select(Camera).where(Camera.code == data.code))
    if existing.scalar_one_or_none():
        raise AppError(ErrorCode.CONFLICT, f"Camera code {data.code} already exists")

    # Parse GeoJSON location
    coords = data.location.get("coordinates")
    if not coords or len(coords) != 2:
        raise AppError(ErrorCode.VALIDATION_ERROR, "location must be GeoJSON Point with [lon, lat]")
    point = WKTElement(f"POINT({coords[0]} {coords[1]})", srid=4326)

    camera = Camera(
        name=data.name,
        code=data.code,
        forest_id=data.forest_id,
        location=point,
        heading_deg=data.heading_deg,
        status=data.status,
        is_simulated=data.is_simulated,
    )
    db.add(camera)
    await db.flush()

    for src in data.sources:
        db.add(CameraSource(camera_id=camera.id, source_type=src.source_type, uri=src.uri, extra=src.extra))

    await db.commit()
    await db.refresh(camera)
    return camera


async def update_camera(db: AsyncSession, camera_id: UUID, data: CameraUpdate) -> Camera | None:
    camera = await get_camera(db, camera_id)
    if not camera:
        return None

    if data.name is not None:
        camera.name = data.name
    if data.forest_id is not None:
        camera.forest_id = data.forest_id
    if data.location is not None:
        coords = data.location.get("coordinates")
        if coords and len(coords) == 2:
            camera.location = WKTElement(f"POINT({coords[0]} {coords[1]})", srid=4326)
    if data.heading_deg is not None:
        camera.heading_deg = data.heading_deg
    if data.status is not None:
        camera.status = data.status
    if data.is_simulated is not None:
        camera.is_simulated = data.is_simulated

    await db.commit()
    await db.refresh(camera)
    return camera


async def delete_camera(db: AsyncSession, camera_id: UUID) -> bool:
    camera = await get_camera(db, camera_id)
    if not camera:
        return False
    # Soft delete: set status to retired
    camera.status = "retired"
    await db.commit()
    return True


async def add_camera_source(db: AsyncSession, camera_id: UUID, data: CameraSourceCreate) -> CameraSource | None:
    camera = await get_camera(db, camera_id)
    if not camera:
        return None
    source = CameraSource(camera_id=camera_id, source_type=data.source_type, uri=data.uri, extra=data.extra)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source