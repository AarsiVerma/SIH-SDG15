"""SOS API."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.sos_service import trigger_sos
from app.schemas.incident import IncidentRead

router = APIRouter(prefix="/sos", tags=["sos"])


@router.post("/rangers/{ranger_id}/sos", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def trigger_sos_endpoint(
    ranger_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    incident = await trigger_sos(db, ranger_id)
    return incident