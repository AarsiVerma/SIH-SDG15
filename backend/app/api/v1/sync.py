"""Sync batch API for edge-to-central sync."""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models import (
    Detection, Track, Event, Incident, Evidence,
    Camera, Ranger, RangerLocation, SyncOutbox
)
from app.models.enums import IngestJobStatus

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncItem(BaseModel):
    idempotency_key: str
    kind: str  # detection|track|event|incident|evidence
    payload: dict


class SyncBatchRequest(BaseModel):
    items: List[SyncItem]


class SyncBatchResponse(BaseModel):
    results: List[dict]


KIND_MODELS = {
    "detection": Detection,
    "track": Track,
    "event": Event,
    "incident": Incident,
    "evidence": Evidence,
}


@router.post("/batch", response_model=SyncBatchResponse)
async def sync_batch(
    data: SyncBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    results = []

    for item in data.items:
        try:
            # Check if already synced (idempotency)
            existing = await db.execute(
                select(SyncOutbox).where(SyncOutbox.idempotency_key == item.idempotency_key)
            )
            if existing.scalar_one_or_none():
                results.append({"idempotency_key": item.idempotency_key, "status": "duplicate"})
                continue

            Model = KIND_MODELS.get(item.kind)
            if not Model:
                results.append({"idempotency_key": item.idempotency_key, "status": "error", "error": "Unknown kind"})
                continue

            # Create or update
            obj = Model(**item.payload)
            db.add(obj)
            await db.commit()

            # Record in outbox
            from app.models import SyncOutbox
            from uuid import uuid4
            outbox = SyncOutbox(
                id=uuid4(),
                idempotency_key=item.idempotency_key,
                payload=item.payload,
                created_at=datetime.utcnow(),
                synced_at=datetime.utcnow(),
                attempts=1,
            )
            db.add(outbox)
            await db.commit()

            results.append({"idempotency_key": item.idempotency_key, "status": "accepted"})

        except Exception as e:
            results.append({"idempotency_key": item.idempotency_key, "status": "error", "error": str(e)})

    return SyncBatchResponse(results=results)