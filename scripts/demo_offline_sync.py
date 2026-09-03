#!/usr/bin/env python3
"""Offline sync demo: simulate edge collection then sync to central."""

import asyncio
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from app.sync.outbox import Outbox
from app.core.config import get_settings

async def main():
    print("=== VANRAKSHA Offline Sync Demo ===\n")

    # Create edge outbox
    outbox = Outbox()
    print(f"Outbox: {outbox.db_path}")

    # Simulate edge collection (no central connection)
    print("\n1. Edge mode: collecting detections offline...")
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
        print(f"   Queued detection {i+1} (key: {key[:8]}...)")

    print(f"\n2. Outbox now has {len(outbox.get_pending())} pending items")

    # Simulate network restored - sync to central
    print("\n3. Network restored: syncing to central...")
    pending = outbox.get_pending()
    for item in pending:
        print(f"   Syncing {item['kind']} (key: {item['idempotency_key'][:8]}...)")
        # In real scenario, would POST to /api/v1/sync/batch
        outbox.mark_synced(item['idempotency_key'])
        print(f"   Marked as synced")

    print(f"\n4. Outbox now has {len(outbox.get_pending())} pending items")
    print("\n✓ Demo complete! Items were queued offline and synced when connection restored.")

if __name__ == "__main__":
    asyncio.run(main())