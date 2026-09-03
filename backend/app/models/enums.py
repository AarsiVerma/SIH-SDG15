"""Shared enums."""
import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FOREST_OFFICER = "FOREST_OFFICER"
    RANGER = "RANGER"
    VIEWER = "VIEWER"


class CameraStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    OFFLINE = "offline"
    RETIRED = "retired"
    DEGRADED = "degraded"


class SourceType(str, enum.Enum):
    FILE = "file"
    WEBCAM = "webcam"
    RTSP = "rtsp"
    OTHER = "other"


class ZoneType(str, enum.Enum):
    PATROL = "patrol"
    RESTRICTED = "restricted"
    CORRIDOR = "corridor"
    BUFFER = "buffer"
    OTHER = "other"


class IncidentStatus(str, enum.Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    DISPATCHED = "DISPATCHED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventType(str, enum.Enum):
    PERSON_DETECTED = "person_detected"
    VEHICLE_DETECTED = "vehicle_detected"
    ANIMAL_DETECTED = "animal_detected"
    SMOKE_DETECTED = "smoke_detected"
    FIRE_DETECTED = "fire_detected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SUSPICIOUS_ACTIVITY_HIGH_RISK = "suspicious_activity_high_risk"
    WILDLIFE_UNUSUAL_MOVEMENT = "wildlife_unusual_movement"
    CAMERA_TAMPERING_SUSPECTED = "camera_tampering_suspected"
    CAMERA_FAILURE_SUSPECTED = "camera_failure_suspected"
    RANGER_SOS = "ranger_sos"
    RESTRICTED_ZONE_ACTIVITY = "restricted_zone_activity"


class EvidenceKind(str, enum.Enum):
    FRAME = "frame"
    CLIP = "clip"
    JSON = "json"


class CameraHealthState(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    WS = "ws"


class IngestJobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class IncidentOutcome(str, enum.Enum):
    CONFIRMED_ISSUE = "confirmed_issue"
    FALSE_POSITIVE = "false_positive"
    DUPLICATE = "duplicate"
    TRAINING = "training"
    OTHER = "other"