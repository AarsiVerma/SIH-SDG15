"""Structured JSON-capable logging with request-scoped context."""
import json
import logging
from contextvars import ContextVar

from app.core.config import get_settings

request_id_var: ContextVar = ContextVar("request_id", default="-")
camera_id_var: ContextVar = ContextVar("camera_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
            "camera_id": camera_id_var.get(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Never log raw image bytes or JWTs."""
    return logging.getLogger(name)


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler()
    if settings.debug:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    else:
        handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.debug else logging.INFO)