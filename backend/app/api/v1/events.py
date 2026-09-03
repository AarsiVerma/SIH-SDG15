"""Event API."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.event import EventRead
from app.schemas.common import Page
from app.services.event_service import list_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=Page[EventRead])
async def list_events_endpoint(
    pagination: Pagination,
    camera_id: Optional[UUID] = Query(None),
    event_type: Optional[str] = Query(None),
    alertable: Optional[bool] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_events(
        db, pagination.limit, pagination.offset, camera_id, event_type, alertable, from_ts, to_ts
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)