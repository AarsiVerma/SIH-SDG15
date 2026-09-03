"""Patrols API."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.models import Patrol, Ranger
from app.schemas.patrol import PatrolRead, PatrolCreate, PatrolUpdate
from app.schemas.common import Page

router = APIRouter(prefix="/patrols", tags=["patrols"])


@router.get("", response_model=Page[PatrolRead])
async def list_patrols(
    pagination: Pagination,
    ranger_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Patrol)
    if ranger_id:
        stmt = stmt.where(Patrol.ranger_id == ranger_id)
    if status:
        stmt = stmt.where(Patrol.status == status)
    if from_ts:
        stmt = stmt.where(Patrol.started_at >= from_ts)
    if to_ts:
        stmt = stmt.where(Patrol.started_at <= to_ts)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Patrol.started_at.desc()).limit(pagination.limit).offset(pagination.offset)
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=PatrolRead, status_code=201)
async def create_patrol(
    data: PatrolCreate,
    db: AsyncSession = Depends(get_db),
):
    ranger = await db.get(Ranger, data.ranger_id)
    if not ranger:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")

    patrol = Patrol(
        ranger_id=data.ranger_id,
        started_at=data.started_at,
        status="active",
    )
    db.add(patrol)
    await db.commit()
    await db.refresh(patrol)
    return patrol


@router.patch("/{patrol_id}", response_model=PatrolRead)
async def update_patrol(
    patrol_id: UUID,
    data: PatrolUpdate,
    db: AsyncSession = Depends(get_db),
):
    patrol = await db.get(Patrol, patrol_id)
    if not patrol:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Patrol not found")

    if data.ended_at is not None:
        patrol.ended_at = data.ended_at
    if data.status is not None:
        patrol.status = data.status
    if data.route_geom is not None:
        # Would parse GeoJSON LineString
        pass

    await db.commit()
    await db.refresh(patrol)
    return patrol


@router.get("/{patrol_id}", response_model=PatrolRead)
async def get_patrol(
    patrol_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    patrol = await db.get(Patrol, patrol_id)
    if not patrol:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Patrol not found")
    return patrol