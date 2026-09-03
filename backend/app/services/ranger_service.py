"""Ranger service."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ranger
from app.schemas.ranger import RangerCreate, RangerUpdate
from app.core.errors import AppError, ErrorCode


async def list_rangers(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    active: Optional[bool] = None,
) -> tuple[list[Ranger], int]:
    stmt = select(Ranger)
    if active is not None:
        stmt = stmt.where(Ranger.active == active)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(total_stmt)).scalar_one()

    stmt = stmt.order_by(Ranger.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_ranger(db: AsyncSession, ranger_id: UUID) -> Ranger | None:
    stmt = select(Ranger).where(Ranger.id == ranger_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_ranger(db: AsyncSession, data: RangerCreate) -> Ranger:
    existing = await db.execute(select(Ranger).where(Ranger.badge_code == data.badge_code))
    if existing.scalar_one_or_none():
        raise AppError(ErrorCode.CONFLICT, f"Badge code {data.badge_code} already exists")

    ranger = Ranger(
        badge_code=data.badge_code,
        name=data.name,
        is_simulated=data.is_simulated,
        active=data.active,
    )
    db.add(ranger)
    await db.commit()
    await db.refresh(ranger)
    return ranger


async def update_ranger(db: AsyncSession, ranger_id: UUID, data: RangerUpdate) -> Ranger | None:
    ranger = await get_ranger(db, ranger_id)
    if not ranger:
        return None

    if data.name is not None:
        ranger.name = data.name
    if data.is_simulated is not None:
        ranger.is_simulated = data.is_simulated
    if data.active is not None:
        ranger.active = data.active

    await db.commit()
    await db.refresh(ranger)
    return ranger