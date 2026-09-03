"""Location API."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.location import LocationCreate, LocationRead, RangerLocationRead
from app.services.location_service import ingest_location, latest_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/rangers/{ranger_id}/location", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def ingest_ranger_location(
    ranger_id: UUID,
    data: LocationCreate,
    db: AsyncSession = Depends(get_db),
):
    loc = await ingest_location(
        db, ranger_id, data.lat, data.lon, data.captured_at, data.source
    )
    return LocationRead(
        id=loc.id,
        ranger_id=loc.ranger_id,
        captured_at=loc.captured_at,
        geom={"type": "Point", "coordinates": [float(loc.geom.x), float(loc.geom.y)]},
        source=loc.source,
    )


@router.get("/rangers/locations/latest", response_model=List[RangerLocationRead])
async def get_latest_locations(
    db: AsyncSession = Depends(get_db),
):
    locations = await latest_locations(db)
    return [
        RangerLocationRead(
            id=loc.id,
            ranger_id=loc.ranger_id,
            captured_at=loc.captured_at,
            geom={"type": "Point", "coordinates": [float(loc.geom.x), float(loc.geom.y)]},
            source=loc.source,
        )
        for loc in locations
    ]