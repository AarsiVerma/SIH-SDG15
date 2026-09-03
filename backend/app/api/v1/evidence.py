"""Evidence API with proper authorization."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app.api.deps import PaginationParams, Pagination, RequireViewer
from app.db.session import get_db
from app.schemas.evidence import EvidenceRead
from app.schemas.common import Page
from app.services.evidence_service import get_evidence, list_evidence
from app.models import User
from app.core.config import get_settings
from app.evidence.local_store import LocalEvidenceStore

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", response_model=Page[EvidenceRead])
async def list_evidence_endpoint(
    pagination: Pagination,
    incident_id: Optional[UUID] = Query(None),
    event_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireViewer),
):
    items = await list_evidence(db, pagination.limit, pagination.offset, incident_id, event_id)
    return Page(items=items, total=len(items), limit=pagination.limit, offset=pagination.offset)


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence_endpoint(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireViewer),
):
    evidence = await get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.get("/{evidence_id}/file")
async def get_evidence_file(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RequireViewer),
):
    """Serve evidence file with authorization check."""
    evidence = await get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Additional authorization: check if user can access this incident's evidence
    settings = get_settings()
    if settings.restrict_evidence:
        # For MVP, all authenticated users with VIEWER+ role can access
        # In production, add more granular checks (assigned ranger, zone, etc.)
        pass

    # Resolve file path
    if not evidence.storage_uri.startswith("file://"):
        raise HTTPException(status_code=500, detail="Unsupported storage")

    store = LocalEvidenceStore(settings.evidence_dir)
    filepath = store.get_path(
        type("obj", (), {"storage_uri": evidence.storage_uri, "sha256": evidence.sha256})()
    )

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Verify SHA-256 integrity
    if not store.verify(type("obj", (), {"storage_uri": evidence.storage_uri, "sha256": evidence.sha256})()):
        raise HTTPException(status_code=500, detail="Evidence integrity check failed")

    # Audit log would go here
    return FileResponse(
        filepath,
        media_type="image/jpeg",
        filename=f"{evidence.sha256}.jpg",
        headers={"Cache-Control": "private, max-age=3600"}
    )