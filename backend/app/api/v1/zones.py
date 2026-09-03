"""Zone and Forest API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.zone import ZoneCreate, ZoneRead, ZoneUpdate, ForestCreate, ForestRead
from app.schemas.common import Page
from app.services.zone_service import (
    list_zones, get_zone, create_zone, update_zone, list_forests, create_forest,
)

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=Page[ZoneRead])
async def list_zones_endpoint(
    pagination: Pagination,
    forest_id: Optional[UUID] = Query(None),
    restricted: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_zones(db, pagination.limit, pagination.offset, forest_id, restricted)
    from app.schemas.zone import ZoneRead
    zone_reads = [ZoneRead.from_orm(z) for z in items]
    return Page(items=zone_reads, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
async def create_zone_endpoint(
    data: ZoneCreate,
    db: AsyncSession = Depends(get_db),
):
    zone = await create_zone(db, data)
    from app.schemas.zone import ZoneRead
    return ZoneRead.from_orm(zone)


@router.get("/{zone_id}", response_model=ZoneRead)
async def get_zone_endpoint(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    zone = await get_zone(db, zone_id)
    if not zone:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Zone not found")
    from app.schemas.zone import ZoneRead
    return ZoneRead.from_orm(zone)


@router.patch("/{zone_id}", response_model=ZoneRead)
async def update_zone_endpoint(
    zone_id: UUID,
    data: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    zone = await update_zone(db, zone_id, data)
    if not zone:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Zone not found")
    from app.schemas.zone import ZoneRead
    return ZoneRead.from_orm(zone)


# Forest endpoints
forests_router = APIRouter(prefix="/forests", tags=["forests"])


@forests_router.get("", response_model=Page[ForestRead])
async def list_forests_endpoint(
    pagination: Pagination,
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_forests(db, pagination.limit, pagination.offset)
    from app.schemas.zone import ForestRead
    forest_reads = [ForestRead.from_orm(f) for f in items]
    return Page(items=forest_reads, total=total, limit=pagination.limit, offset=pagination.offset)


@forests_router.post("", response_model=ForestRead, status_code=status.HTTP_201_CREATED)
async def create_forest_endpoint(
    data: ForestCreate,
    db: AsyncSession = Depends(get_db),
):
    forest = await create_forest(db, data)
    from app.schemas.zone import ForestRead
    return ForestRead.from_orm(forest)