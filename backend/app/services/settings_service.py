"""System settings service."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SystemSettings
from app.schemas.settings import SystemSettingsUpdate
from app.core.errors import AppError, ErrorCode


async def get_setting(db: AsyncSession, key: str) -> SystemSettings | None:
    stmt = select(SystemSettings).where(SystemSettings.key == key)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_setting(db: AsyncSession, key: str, data: SystemSettingsUpdate) -> SystemSettings:
    setting = await get_setting(db, key)
    if not setting:
        setting = SystemSettings(key=key, value=data.value)
        db.add(setting)
    else:
        setting.value = data.value
    await db.commit()
    await db.refresh(setting)
    return setting


async def validate_risk_weights(value: dict) -> None:
    """Validate risk_weights schema."""
    required = {"max_score", "levels", "factors"}
    if not all(k in value for k in required):
        raise AppError(ErrorCode.VALIDATION_ERROR, f"risk_weights must contain {required}")

    levels = value["levels"]
    if not isinstance(levels, dict) or not all(k in levels for k in ("low", "medium", "high", "critical")):
        raise AppError(ErrorCode.VALIDATION_ERROR, "levels must have low, medium, high, critical")

    factors = value["factors"]
    if not isinstance(factors, list):
        raise AppError(ErrorCode.VALIDATION_ERROR, "factors must be a list")
    for f in factors:
        if not all(k in f for k in ("code", "delta")):
            raise AppError(ErrorCode.VALIDATION_ERROR, "each factor must have code and delta")