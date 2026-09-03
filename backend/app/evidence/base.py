"""EvidenceStore protocol and reference."""
from dataclasses import dataclass
from typing import Protocol
from pathlib import Path


@dataclass
class EvidenceRef:
    sha256: str
    storage_uri: str  # file:// relative path
    nbytes: int


class EvidenceStore(Protocol):
    def put_bytes(self, data: bytes, *, suffix: str) -> EvidenceRef: ...