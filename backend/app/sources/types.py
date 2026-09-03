"""Video source metadata."""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class VideoSourceMetadata:
    fps_nominal: float
    uri_redacted: str
    source_type: str
    width: int
    height: int