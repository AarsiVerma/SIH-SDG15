"""Risk factor configuration and defaults."""
from typing import List, Dict, Any

from app.core.config import get_settings


DEFAULT_RISK_WEIGHTS = {
    "max_score": 100,
    "levels": {
        "low": [0, 30],
        "medium": [31, 60],
        "high": [61, 80],
        "critical": [81, 100],
    },
    "factors": [
        {"code": "restricted_zone", "delta": 25},
        {"code": "nighttime", "delta": 10},
        {"code": "vehicle", "delta": 15},
        {"code": "suspicious_pattern", "delta": 25},
        {"code": "wildlife_nearby", "delta": 15},
        {"code": "repeated_movement", "delta": 10},
        {"code": "camera_tampering", "delta": 20},
        {"code": "authorized_ranger", "delta": -40},
    ],
}


def get_risk_weights() -> Dict[str, Any]:
    """Get risk weights from settings (DB) or defaults."""
    settings = get_settings()
    # In production, would load from system_settings table
    # For now return defaults
    return DEFAULT_RISK_WEIGHTS


def get_incident_min_level() -> str:
    settings = get_settings()
    return settings.incident_min_level