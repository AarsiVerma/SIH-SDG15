"""Centralized application settings loaded from environment (.env)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_MODELS_DIR = ROOT_DIR / "models"
DEFAULT_EVIDENCE_DIR = ROOT_DIR / "evidence"


class Settings(BaseSettings):
    """Typed application settings. No secrets live in source code."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "VANRAKSHA AI"
    debug: bool = False
    environment: str = "development"

    database_url: str = "postgresql+psycopg://vanraksha:vanraksha@localhost:5432/vanraksha"
    secret_key: str = "change-me-in-production"
    cors_origins: list[str] = ["http://localhost:3000"]

    edge_mode: bool = False
    demo_mode: bool = False
    allow_agpl: bool = False

    models_dir: Path = DEFAULT_MODELS_DIR
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR
    sample_fps: float = 2.0

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    night_start: str = "18:00"
    night_end: str = "06:00"
    timezone: str = "Asia/Kolkata"

    ranger_proximity_radius_m: float = 500.0
    ranger_location_skew_minutes: int = 15

    detector_backend: str = "dummy"  # dummy | onnx
    tracker_backend: str = "iou"  # iou | bytetrack
    species_backend: str = "null"  # null | megadetector

    offline_after_seconds: int = 30
    incident_min_level: str = "medium"

    restrict_evidence: bool = True

    sync_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def check_secret_key() -> None:
    """Fail fast if SECRET_KEY is left at default in production."""
    settings = get_settings()
    if settings.environment == "production" and settings.secret_key in ("change-me-in-production", "changeme-in-production", "changeme", ""):
        raise RuntimeError("SECRET_KEY must be overridden in production")