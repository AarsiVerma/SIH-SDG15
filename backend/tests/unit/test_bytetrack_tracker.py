import pytest

pytestmark = pytest.mark.postgres

"""Tests for the ByteTrack tracker."""
from datetime import datetime, timedelta
from uuid import uuid4
import numpy as np

from app.vision.bytetrack_tracker import ByteTrackTracker, iou
from app.vision.tracker_base import TrackUpdate
from app.vision.types import DetectionCandidate
from app.sources.base import Frame


@pytest.fixture
def tracker():
    """Create a ByteTrack tracker with default settings."""
    return ByteTrackTracker(
        track_thresh=0.5,
        match_thresh=0.8,
        track_buffer=30,
        min_box_area=100,
        min_hits=3,
    )


@pytest.fixture
def sample_frame():
    """Create a sample frame."""
    return Frame(
        camera_id=uuid4(),
        source_id=None,
        captured_at=datetime.utcnow(),
        seq=1,
        image_bgr=None,
        width=640,
        height=480,
    )


@pytest.fixture
def person_detection():
    """Create a person detection candidate."""
    return DetectionCandidate(
        class_name="person",
        class_id=0,
        confidence=0.85,
        bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
        detector_id="test",
        model_version="1.0",
    )


@pytest.fixture
def vehicle_detection():
    """Create a vehicle detection candidate."""
    return DetectionCandidate(
        class_name="vehicle",
        class_id=1,
        confidence=0.90,
        bbox_xyxy=(300.0, 200.0, 500.0, 400.0),
        detector_id="test",
        model_version="1.0",
    )


class TestIoU:
    """Test IoU calculation."""

    def test_perfect_overlap(self):
        """Test IoU of identical boxes is 1.0."""
        box = (100, 100, 200, 200)
        assert iou(box, box) == 1.0

    def test_no_overlap(self):
        """Test IoU of non-overlapping boxes is 0."""
        box1 = (100, 100, 200, 200)
        box2 = (300, 300, 400, 400)
        assert iou(box1, box2) == 0.0

    def test_partial_overlap(self):
        """Test IoU of partially overlapping boxes."""
        box1 = (100, 100, 200, 200)
        box2 = (150, 150, 250, 250)
        result = iou(box1, box2)
        assert 0 < result < 1


class TestByteTrackTracker:
    """Test ByteTrack tracker functionality."""

    def test_new_object_creates_track(self, tracker, sample_frame, person_detection):
        """Test new detection creates a track after min_hits."""
        # First frame - track created but not confirmed (hit_count=1)
        updates = tracker.update(sample_frame, [person_detection])
        assert len(updates) == 0

        # Second frame - same detection
        sample_frame.seq = 2
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [person_detection])
        assert len(updates) == 0

        # Third frame - track confirmed (hit_count=3)
        sample_frame.seq = 3
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [person_detection])
        assert len(updates) == 1
        assert updates[0].class_name == "person"
        assert updates[0].track_id == 1

    def test_continuing_object_maintains_id(self, tracker, sample_frame, person_detection):
        """Test continuing object maintains same track ID."""
        # Create confirmed track
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection])

        # Move object slightly
        moved_detection = DetectionCandidate(
            class_name="person",
            class_id=0,
            confidence=0.85,
            bbox_xyxy=(110.0, 110.0, 210.0, 310.0),
            detector_id="test",
            model_version="1.0",
        )
        sample_frame.seq = 4
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [moved_detection])
        assert len(updates) == 1
        assert updates[0].track_id == 1

    def test_multiple_objects_get_different_ids(self, tracker, sample_frame, person_detection, vehicle_detection):
        """Test multiple objects get different track IDs."""
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection, vehicle_detection])

        assert len(tracker.tracks) == 2

    def test_disappearing_object_ages_out(self, tracker, sample_frame, person_detection):
        """Test object that disappears ages out after track_buffer."""
        # Create confirmed track
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection])

        # Stop detecting for track_buffer + 1 frames
        for i in range(31):
            sample_frame.seq = 4 + i
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [])

        # Track should be removed
        assert len(tracker.tracks) == 0

    def test_class_aware_matching(self, tracker, sample_frame, person_detection):
        """Test tracks only match same class."""
        # Create person track
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection])

        # Try to match with vehicle at same location
        vehicle_at_person_loc = DetectionCandidate(
            class_name="vehicle",
            class_id=1,
            confidence=0.90,
            bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
            detector_id="test",
            model_version="1.0",
        )
        sample_frame.seq = 4
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [vehicle_at_person_loc])

        # Should create new track for vehicle, not match person track
        assert len(tracker.tracks) == 2

    def test_low_confidence_detections_handled(self, tracker, sample_frame):
        """Test low confidence detections are handled separately."""
        high_conf = DetectionCandidate(
            class_name="person",
            class_id=0,
            confidence=0.85,
            bbox_xyxy=(100.0, 100.0, 200.0, 300.0),
            detector_id="test",
            model_version="1.0",
        )
        low_conf = DetectionCandidate(
            class_name="person",
            class_id=0,
            confidence=0.30,  # Below track_thresh
            bbox_xyxy=(105.0, 105.0, 205.0, 305.0),
            detector_id="test",
            model_version="1.0",
        )

        # First create confirmed track with high conf
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [high_conf])

        # Then add low confidence detection nearby
        sample_frame.seq = 4
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [low_conf])
        # Should still have the track
        assert len(updates) == 1

    def test_invalid_bbox_filtered(self, tracker, sample_frame):
        """Test invalid bounding boxes are filtered."""
        invalid_detection = DetectionCandidate(
            class_name="person",
            class_id=0,
            confidence=0.85,
            bbox_xyxy=(200.0, 200.0, 100.0, 100.0),  # x2 < x1
            detector_id="test",
            model_version="1.0",
        )
        sample_frame.seq = 1
        updates = tracker.update(sample_frame, [invalid_detection])
        assert len(updates) == 0
        assert len(tracker.tracks) == 0

    def test_small_bbox_filtered(self, tracker, sample_frame):
        """Test boxes below min_box_area are filtered."""
        small_detection = DetectionCandidate(
            class_name="person",
            class_id=0,
            confidence=0.85,
            bbox_xyxy=(100.0, 100.0, 105.0, 105.0),  # 25 area < 100 min
            detector_id="test",
            model_version="1.0",
        )
        sample_frame.seq = 1
        updates = tracker.update(sample_frame, [small_detection])
        assert len(updates) == 0

    def test_confidence_averaging(self, tracker, sample_frame, person_detection):
        """Test confidence is averaged over hits."""
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection])

        sample_frame.seq = 4
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [person_detection])
        # Confidence should be average of all hits
        assert abs(updates[0].confidence - 0.85) < 0.01

    def test_track_update_fields(self, tracker, sample_frame, person_detection):
        """Test TrackUpdate has all required fields."""
        for i in range(3):
            sample_frame.seq = i + 1
            sample_frame.captured_at += timedelta(seconds=1)
            tracker.update(sample_frame, [person_detection])

        sample_frame.seq = 4
        sample_frame.captured_at += timedelta(seconds=1)
        updates = tracker.update(sample_frame, [person_detection])
        
        update = updates[0]
        assert isinstance(update.track_id, int)
        assert update.class_name == "person"
        assert isinstance(update.confidence, float)
        assert isinstance(update.bbox_xyxy, tuple)
        assert len(update.bbox_xyxy) == 4
        assert isinstance(update.centroid, tuple)
        assert len(update.centroid) == 2
        assert isinstance(update.first_seen, datetime)
        assert isinstance(update.last_seen, datetime)
        assert update.camera_id == sample_frame.camera_id