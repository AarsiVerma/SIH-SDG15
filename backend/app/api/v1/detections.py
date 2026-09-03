"""Detection and Taxonomy API."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.detection import DetectionRead, TaxonomyClass, TAXONOMY_CLASSES
from app.schemas.common import Page
from app.services.detection_service import list_detections

router = APIRouter(prefix="/detections", tags=["detections"])


@router.get("", response_model=Page[DetectionRead])
async def list_detections_endpoint(
    pagination: Pagination,
    camera_id: Optional[UUID] = Query(None),
    class_name: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None),
    to_ts: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_detections(
        db, pagination.limit, pagination.offset, camera_id, class_name, from_ts, to_ts
    )
    return Page(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get("/taxonomy")
async def get_taxonomy():
    return {"classes": [c.model_dump() for c in TAXONOMY_CLASSES]}