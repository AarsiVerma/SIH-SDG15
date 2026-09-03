"""FrameSampler tests."""
from datetime import datetime, timedelta
from uuid import uuid4

import numpy as np

from app.sources.base import Frame
from app.pipeline.sampler import FrameSampler


def make_frame(seq: int, seconds_offset: float = 0) -> Frame:
    base = datetime(2026, 1, 1, 12, 0, 0)
    return Frame(
        camera_id=uuid4(),
        source_id=uuid4(),
        captured_at=base + timedelta(seconds=seconds_offset),
        seq=seq,
        image_bgr=np.zeros((480, 640, 3), dtype=np.uint8),
        width=640,
        height=480,
    )


def test_sampler_keeps_first_frame():
    sampler = FrameSampler(target_fps=2.0)  # 0.5s interval
    frame = make_frame(1, 0.0)
    assert sampler.should_keep(frame) is True


def test_sampler_respects_interval():
    sampler = FrameSampler(target_fps=2.0)  # 0.5s interval
    f1 = make_frame(1, 0.0)
    f2 = make_frame(2, 0.2)  # Too soon
    f3 = make_frame(3, 0.5)  # At interval
    f4 = make_frame(4, 0.7)  # Too soon

    assert sampler.should_keep(f1) is True
    assert sampler.should_keep(f2) is False
    assert sampler.should_keep(f3) is True
    assert sampler.should_keep(f4) is False


def test_sampler_reset():
    sampler = FrameSampler(target_fps=10.0)  # 0.1s interval
    f1 = make_frame(1, 0.0)
    f2 = make_frame(2, 0.05)

    assert sampler.should_keep(f1) is True
    assert sampler.should_keep(f2) is False

    sampler.reset()
    assert sampler.should_keep(f2) is True  # After reset, first frame kept