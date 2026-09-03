"""FileVideoSource tests."""
import pytest
import cv2
import numpy as np
from pathlib import Path
from uuid import uuid4

from app.sources.file_source import FileVideoSource
from app.core.config import get_settings


def create_test_video(path: Path, num_frames: int = 5, fps: float = 10.0) -> None:
    """Create a synthetic test video."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(path), fourcc, fps, (640, 480))
    for i in range(num_frames):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, f"Frame {i}", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        out.write(frame)
    out.release()


def test_file_source_reads_frames(tmp_path):
    video_path = tmp_path / "test.mp4"
    create_test_video(video_path, num_frames=5)

    camera_id = uuid4()
    source = FileVideoSource(camera_id=camera_id, path=video_path, loop=False)
    source.open()

    frames = []
    while True:
        frame = source.read_frame()
        if frame is None:
            break
        frames.append(frame)

    assert len(frames) == 5
    assert frames[0].camera_id == camera_id
    assert frames[0].width == 640
    assert frames[0].height == 480
    assert frames[0].seq == 1
    assert frames[-1].seq == 5

    source.close()


def test_file_source_loop(tmp_path):
    video_path = tmp_path / "test_loop.mp4"
    create_test_video(video_path, num_frames=3)

    camera_id = uuid4()
    source = FileVideoSource(camera_id=camera_id, path=video_path, loop=True)
    source.open()

    frames = []
    for _ in range(7):  # Read more than video length
        frame = source.read_frame()
        if frame is None:
            break
        frames.append(frame)

    assert len(frames) == 7  # Should loop
    # seq continues incrementing across loops
    assert frames[3].seq == 4  # 4th frame overall (wrapped)

    source.close()


def test_file_source_missing_file():
    camera_id = uuid4()
    source = FileVideoSource(camera_id=camera_id, path="/nonexistent/video.mp4")
    with pytest.raises(Exception):  # AppError
        source.open()