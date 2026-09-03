"""System settings schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SystemSettingsBase(BaseModel):
    key: str
    value: dict[str, Any]


class SystemSettingsUpdate(BaseModel):
    value: dict[str, Any]


class SystemSettingsRead(SystemSettingsBase):
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)