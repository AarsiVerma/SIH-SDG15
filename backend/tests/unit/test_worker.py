"""Tests for the worker module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.worker import Worker


@pytest.mark.asyncio
async def test_worker_initialization():
    """Test worker initializes with correct defaults."""
    worker = Worker(poll_interval=5.0, max_concurrent=1)
    assert worker.poll_interval == 5.0
    assert worker.max_concurrent == 1
    assert worker._running is False


@pytest.mark.asyncio
async def test_worker_shutdown():
    """Test worker shutdown sets _running to False."""
    worker = Worker()
    worker._running = True
    worker._shutdown()
    assert worker._running is False


# Note: Full integration tests for worker require database and are in e2e_scenarios