"""Local hashed evidence store."""
import hashlib
import os
from pathlib import Path
from typing import Optional

from app.evidence.base import EvidenceStore, EvidenceRef
from app.core.config import get_settings


class LocalEvidenceStore:
    """Filesystem-based evidence store with SHA-256 content addressing."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or get_settings().evidence_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, data: bytes, *, suffix: str = ".jpg") -> EvidenceRef:
        sha256 = hashlib.sha256(data).hexdigest()
        # Shard by first 4 chars: ab/cd/efgh...
        rel_dir = self.base_dir / sha256[:2] / sha256[2:4]
        rel_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{sha256}{suffix}"
        filepath = rel_dir / filename

        with open(filepath, "wb") as f:
            f.write(data)

        return EvidenceRef(
            sha256=sha256,
            storage_uri=f"file://{filepath.relative_to(self.base_dir.parent)}",
            nbytes=len(data),
        )

    def get_path(self, ref: EvidenceRef) -> Path:
        """Resolve storage_uri to absolute path."""
        if not ref.storage_uri.startswith("file://"):
            raise ValueError("Only file:// URIs supported")
        rel = ref.storage_uri[len("file://"):]
        return self.base_dir.parent / rel

    def verify(self, ref: EvidenceRef) -> bool:
        """Verify file matches SHA-256."""
        path = self.get_path(ref)
        if not path.exists():
            return False
        with open(path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest() == ref.sha256