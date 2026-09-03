"""Ranger management API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.ranger import RangerCreate, RangerRead, RangerUpdate
from app.schemas.common import Page
from app.services.ranger_service import list_rangers, get_ranger, create_ranger, update_ranger

router = APIRouter(prefix="/rangers", tags=["rangers"])


@router.get("", response_model=Page[RangerRead])
async def list_rangers_endpoint(
    pagination: Pagination,
    active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_rangers(db, pagination.limit, pagination.offset, active)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.post("", response_model=RangerRead, status_code=status.HTTP_201_CREATED)
async def create_ranger_endpoint(
    data: RangerCreate,
    db: AsyncSession = Depends(get_db),
):
    ranger = await create_ranger(db, data)
    return ranger


@router.get("/{ranger_id}", response_model=RangerRead)
async def get_ranger_endpoint(
    ranger_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    ranger = await get_ranger(db, ranger_id)
    if not ranger:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")
    return ranger


@router.patch("/{ranger_id}", response_model=RangerRead)
async def update_ranger_endpoint(
    ranger_id: UUID,
    data: RangerUpdate,
    db: AsyncSession = Depends(get_db),
):
    ranger = await update_ranger(db, ranger_id, data)
    if not ranger:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")
    return ranger