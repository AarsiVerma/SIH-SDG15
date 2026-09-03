"""System settings API (admin)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.settings import SystemSettingsUpdate, SystemSettingsRead
from app.services.settings_service import get_setting, update_setting, validate_risk_weights

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{key}", response_model=SystemSettingsRead)
async def get_setting_endpoint(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    setting = await get_setting(db, key)
    if not setting:
        from app.core.errors import AppError, ErrorCode
        raise AppError(ErrorCode.NOT_FOUND, f"Setting {key} not found")
    return setting


@router.put("/{key}", response_model=SystemSettingsRead)
async def update_setting_endpoint(
    key: str,
    data: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    # Validate risk_weights if that's the key
    if key == "risk_weights":
        await validate_risk_weights(data.value)

    setting = await update_setting(db, key, data)
    return setting