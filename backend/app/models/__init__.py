"""Models package — all ORM models imported for Alembic autogenerate."""
from app.models.user import User
from app.models.forest import ForestArea
from app.models.zone import Zone
from app.models.camera import Camera, CameraSource
from app.models.detection import Detection
from app.models.track import Track, TrackPoint, TrackStatus
from app.models.event import (
    Event,
    EventFactor,
    EventTrack,
    Incident,
    IncidentEvent,
    IncidentStatusHistory,
    Evidence,
)
from app.models.ranger import (
    Ranger,
    RangerLocation,
    Patrol,
    CameraHealth,
    Notification,
    AuditLog,
    SystemSettings,
    SyncOutbox,
)
from app.models.ingest_job import IngestJob, IngestJobStatus
from app.models.wildlife import WildlifeObservation
from app.models.incident_outcome import IncidentOutcomeRecord, IncidentOutcome
from app.models.enums import (
    UserRole,
    CameraStatus,
    SourceType,
    ZoneType,
    IncidentStatus,
    RiskLevel,
    EventType,
    EvidenceKind,
    CameraHealthState,
    NotificationChannel,
)

__all__ = [
    "User",
    "ForestArea",
    "Zone",
    "Camera",
    "CameraSource",
    "Detection",
    "Track",
    "TrackPoint",
    "TrackStatus",
    "Event",
    "EventFactor",
    "EventTrack",
    "Incident",
    "IncidentEvent",
    "IncidentStatusHistory",
    "Evidence",
    "Ranger",
    "RangerLocation",
    "Patrol",
    "CameraHealth",
    "Notification",
    "AuditLog",
    "SystemSettings",
    "SyncOutbox",
    "IngestJob",
    "IngestJobStatus",
    "WildlifeObservation",
    "IncidentOutcomeRecord",
    "IncidentOutcome",
    "UserRole",
    "CameraStatus",
    "SourceType",
    "ZoneType",
    "IncidentStatus",
    "RiskLevel",
    "EventType",
    "EvidenceKind",
    "CameraHealthState",
    "NotificationChannel",
]