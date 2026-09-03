"""Structured JSON-capable logging with request-scoped context."""
import json
import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict

from app.core.config import get_settings

request_id_var: ContextVar = ContextVar("request_id", default="-")
camera_id_var: ContextVar = ContextVar("camera_id", default=None)
job_id_var: ContextVar = ContextVar("job_id", default=None)
incident_id_var: ContextVar = ContextVar("incident_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "camera_id": camera_id_var.get(),
            "job_id": job_id_var.get(),
            "incident_id": incident_id_var.get(),
        }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info", "getMessage"
            ):
                if not key.startswith("_"):
                    payload[key] = value

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        
        return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Never log raw image bytes or JWTs."""
    return logging.getLogger(name)


def log_job_started(job_id: str, camera_id: str, target_fps: float) -> None:
    """Log job start with structured data."""
    logger = get_logger("app.pipeline")
    logger.info("Job started", extra={"job_id": job_id, "camera_id": camera_id, "target_fps": target_fps})


def log_job_completed(job_id: str, camera_id: str, frames: int, detections: int, duration_ms: float) -> None:
    """Log job completion with metrics."""
    logger = get_logger("app.pipeline")
    logger.info("Job completed", extra={
        "job_id": job_id,
        "camera_id": camera_id,
        "frames_processed": frames,
        "detections_created": detections,
        "duration_ms": duration_ms,
    })


def log_job_failed(job_id: str, camera_id: str, error: str) -> None:
    """Log job failure with error details."""
    logger = get_logger("app.pipeline")
    logger.error("Job failed", extra={"job_id": job_id, "camera_id": camera_id, "error": error})


def log_incident_created(incident_id: str, public_id: str, risk_level: str, camera_id: str) -> None:
    """Log incident creation."""
    logger = get_logger("app.incident")
    logger.info("Incident created", extra={
        "incident_id": incident_id,
        "public_id": public_id,
        "risk_level": risk_level,
        "camera_id": camera_id,
    })


def log_incident_updated(incident_id: str, public_id: str, status: str, actor: str) -> None:
    """Log incident status update."""
    logger = get_logger("app.incident")
    logger.info("Incident updated", extra={
        "incident_id": incident_id,
        "public_id": public_id,
        "status": status,
        "actor": actor,
    })


def log_evidence_created(evidence_id: str, incident_id: str, sha256: str) -> None:
    """Log evidence creation with integrity hash."""
    logger = get_logger("app.evidence")
    logger.info("Evidence created", extra={
        "evidence_id": evidence_id,
        "incident_id": incident_id,
        "sha256": sha256,
    })


def log_detector_init(backend: str, model_path: str = None) -> None:
    """Log detector initialization."""
    logger = get_logger("app.vision")
    logger.info("Detector initialized", extra={"backend": backend, "model_path": model_path})


def log_tracker_init(backend: str, params: Dict[str, Any] = None) -> None:
    """Log tracker initialization."""
    logger = get_logger("app.vision")
    logger.info("Tracker initialized", extra={"backend": backend, "params": params})


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if root.handlers:
        return
    
    handler = logging.StreamHandler(sys.stdout)
    if settings.debug:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        ))
    else:
        handler.setFormatter(JsonFormatter())
    
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)