"""Wildlife observations API."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.models import WildlifeObservation, Track
from app.schemas.wildlife import WildlifeObservationRead
from app.schemas.common import Page

router = APIRouter(prefix="/wildlife", tags=["wildlife"])


@router.get("/observations", response_model=Page[WildlifeObservationRead])
async def list_observations(
    pagination: Pagination,
    camera_id: Optional[UUID] = Query(None),
    species: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WildlifeObservation)
    if camera_id:
        stmt = stmt.where(WildlifeObservation.camera_id == camera_id)
    if species:
        stmt = stmt.where(WildlifeObservation.species == species)
    if from_ts:
        stmt = stmt.where(WildlifeObservation.first_seen >= from_ts)
    if to_ts:
        stmt = stmt.where(WildlifeObservation.last_seen <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(WildlifeObservation.first_seen.desc()).limit(pagination.limit).offset(pagination.offset)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/observations/{obs_id}")
async def get_observation(
    obs_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WildlifeObservation).where(WildlifeObservation.id == obs_id)
    result = await db.execute(stmt)
    obs = result.scalar_one_or_none()
    if not obs:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Observation not found")
    return obs