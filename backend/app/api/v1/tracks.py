"""Track API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.track import TrackRead, TrackPointRead
from app.schemas.common import Page
from app.services.track_service import list_tracks, get_track_points

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("", response_model=Page[TrackRead])
async def list_tracks_endpoint(
    pagination: Pagination,
    camera_id: Optional[UUID] = Query(None),
    active: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_tracks(db, pagination.limit, pagination.offset, camera_id, active)
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/{track_id}/points", response_model=list[TrackPointRead])
async def get_track_points_endpoint(
    track_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    points = await get_track_points(db, track_id, limit, offset)
    return points