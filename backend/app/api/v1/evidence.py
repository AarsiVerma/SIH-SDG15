"""Evidence API."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app.api.deps import PaginationParams, Pagination
from app.db.session import get_db
from app.schemas.evidence import EvidenceRead
from app.schemas.common import Page
from app.services.evidence_service import get_evidence, list_evidence

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", response_model=Page[EvidenceRead])
async def list_evidence_endpoint(
    pagination: Pagination,
    incident_id: Optional[UUID] = Query(None),
    event_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from app.services.evidence_service import list_evidence
    items = await list_evidence(db, pagination.limit, pagination.offset, incident_id, event_id)
    return Page(items=items, total=len(items), limit=pagination.limit, offset=pagination.offset)


@router.get("/{evidence_id}", response_model=EvidenceRead)
async def get_evidence_endpoint(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    evidence = await get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    return evidence


@router.get("/{evidence_id}/file")
async def get_evidence_file(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    evidence = await get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")

    # Resolve file path
    if not evidence.storage_uri.startswith("file://"):
        raise HTTPException(500, "Unsupported storage")

    from app.evidence.local_store import LocalEvidenceStore
    from app.core.config import get_settings
    store = LocalEvidenceStore(get_settings().evidence_dir)
    filepath = store.get_path(
        type("obj", (), {"storage_uri": evidence.storage_uri, "sha256": evidence.sha256})()
    )

    if not filepath.exists():
        raise HTTPException(404, "File not found")

    # Audit log would go here
    return FileResponse(filepath, media_type="image/jpeg", filename=f"{evidence.sha256}.jpg")