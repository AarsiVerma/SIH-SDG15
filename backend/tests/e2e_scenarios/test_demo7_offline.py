import pytest
pytestmark = pytest.mark.postgres

"""E2E test for Demo 7: Offline Sync."""
from uuid import uuid4
from datetime import datetime

from app.sync.outbox import Outbox


@pytest.mark.asyncio
async def test_demo7_offline_sync(tmp_path):
    """Edge queues offline, syncs when online."""
    outbox = Outbox(tmp_path / "outbox.sqlite")

    # Queue items offline
    keys = []
    for i in range(3):
        key = outbox.enqueue(
            kind="detection",
            payload={
                "camera_id": str(uuid4()),
                "frame_seq": i,
                "captured_at": datetime.utcnow().isoformat(),
                "class_name": "person",
                "class_id": 0,
                "confidence": 0.85,
                "bbox_xyxy": {"x1": 100, "y1": 100, "x2": 200, "y2": 300},
                "detector_id": "dummy",
                "model_version": "0.1.0",
            }
        )
        keys.append(key)

    pending = outbox.get_pending()
    assert len(pending) == 3

    # Simulate sync
    for item in pending:
        outbox.mark_synced(item["idempotency_key"])

    pending_after = outbox.get_pending()
    assert len(pending_after) == 0

    # Re-sync same keys should be duplicates
    for key in keys:
        key2 = outbox.enqueue(
            kind="detection",
            payload={"test": "duplicate"},
            idempotency_key=key,
        )
        assert key2 == key  # Same idempotency key

    pending_dup = outbox.get_pending()
    assert len(pending_dup) == 0  # Duplicates ignored
