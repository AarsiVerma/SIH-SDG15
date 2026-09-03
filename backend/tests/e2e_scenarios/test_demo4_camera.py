"""E2E test for Demo 4: Camera Failure (health service)."""
import pytest
from datetime import datetime, timedelta

from app.services.health_service import classify_health
from app.models.enums import CameraHealthState


@pytest.mark.asyncio
async def test_demo4_camera_empty_vs_stall():
    """Empty scene ≠ failure; no frames = pipeline_stall."""
    now = datetime.utcnow()
    offline_after = 30

    # Case 1: Frames arriving, no detections → online, no_activity
    state, reason = classify_health(
        last_frame=now - timedelta(seconds=5),
        last_heartbeat=now - timedelta(seconds=5),
        last_detection=now - timedelta(hours=1),
        job_running=True,
    )
    assert state == CameraHealthState.ONLINE.value
    assert reason == "no_activity"

    # Case 2: No frames, job running → pipeline_stall
    state, reason = classify_health(
        last_frame=now - timedelta(seconds=60),
        last_heartbeat=now - timedelta(seconds=60),
        last_detection=now - timedelta(hours=1),
        job_running=True,
    )
    assert state == CameraHealthState.OFFLINE.value
    assert reason == "pipeline_stall"

    # Case 3: No frames, job not running → not_ingesting
    state, reason = classify_health(
        last_frame=now - timedelta(seconds=60),
        last_heartbeat=now - timedelta(seconds=60),
        last_detection=now - timedelta(hours=1),
        job_running=False,
    )
    assert state == CameraHealthState.OFFLINE.value
    assert reason == "not_ingesting"
