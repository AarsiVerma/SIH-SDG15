"""EventEngine - evaluates tracks + context into EventCandidates."""
from typing import List
from datetime import datetime, timedelta
from uuid import UUID

from app.engines.context import ContextProvider
from app.vision.tracker_base import TrackUpdate
from app.engines.event_types import EventCandidate, correlation_key
from app.models.enums import EventType
from app.core.config import get_settings


class EventEngine:
    """Evaluates tracks and context to produce alertable event candidates."""

    # Bucket window for correlation (seconds)
    BUCKET_SECONDS = 120

    def __init__(self, context_provider: ContextProvider, settings=None):
        self.context_provider = context_provider
        self.settings = settings or get_settings()

    def evaluate(
        self,
        tracks: List[TrackUpdate],
        timestamp: datetime,
    ) -> List[EventCandidate]:
        """Main entry: tracks + now -> event candidates."""
        if not tracks:
            return []

        camera_id = tracks[0].camera_id
        ctx = self.context_provider.for_camera(camera_id, timestamp)

        # Group tracks by type for pattern detection
        persons = [t for t in tracks if t.class_name == "person"]
        vehicles = [t for t in tracks if t.class_name == "vehicle"]
        animals = [t for t in tracks if t.class_name == "animal"]
        fires = [t for t in tracks if t.class_name in ("fire", "smoke")]

        candidates = []

        # Person tracks
        for t in persons:
            candidates.append(self._person_event(t, ctx))

        # Vehicle tracks
        for t in vehicles:
            candidates.append(self._vehicle_event(t, ctx))

        # Animal tracks
        for t in animals:
            candidates.append(self._animal_event(t, ctx))

        # Fire/smoke
        for t in fires:
            candidates.append(self._fire_event(t, ctx))

        # Composite: person + vehicle + restricted + night -> suspicious_activity
        if persons and vehicles and ctx.in_restricted and ctx.is_night:
            candidates.append(self._suspicious_composite(persons, vehicles, ctx))

        # Filter: only return alertable candidates for operational events
        # Raw detections (person/vehicle in non-restricted day) are not alertable
        return [c for c in candidates if c.alertable or c.event_type in (
            EventType.FIRE_DETECTED, EventType.SMOKE_DETECTED,
            EventType.SUSPICIOUS_ACTIVITY, EventType.SUSPICIOUS_ACTIVITY_HIGH_RISK,
            EventType.RESTRICTED_ZONE_ACTIVITY, EventType.WILDLIFE_UNUSUAL_MOVEMENT,
            EventType.CAMERA_TAMPERING_SUSPECTED, EventType.CAMERA_FAILURE_SUSPECTED,
            EventType.RANGER_SOS,
        )]

    def _bucket_epoch(self, timestamp: datetime) -> int:
        return int(timestamp.timestamp() // self.BUCKET_SECONDS)

    def _person_event(self, track: TrackUpdate, ctx) -> EventCandidate:
        if ctx.in_restricted:
            return EventCandidate(
                event_type=EventType.RESTRICTED_ZONE_ACTIVITY,
                language_key="restricted_zone_activity",
                track_ids=[track.track_id],
                detection_ids=[],
                window_start=track.first_seen,
                window_end=track.last_seen,
                camera_id=track.camera_id,
                correlation_key=correlation_key(track.camera_id, "restricted", self._bucket_epoch(track.last_seen)),
                geometry=ctx.geometry,
                alertable=True,
                payload={"night": ctx.is_night, "track_id": track.track_id},
            )
        elif ctx.is_night:
            return EventCandidate(
                event_type=EventType.SUSPICIOUS_ACTIVITY,
                language_key="suspicious_activity",
                track_ids=[track.track_id],
                detection_ids=[],
                window_start=track.first_seen,
                window_end=track.last_seen,
                camera_id=track.camera_id,
                correlation_key=correlation_key(track.camera_id, "suspicious", self._bucket_epoch(track.last_seen)),
                geometry=ctx.geometry,
                alertable=True,
                payload={"night": True, "track_id": track.track_id},
            )
        else:
            return EventCandidate(
                event_type=EventType.PERSON_DETECTED,
                language_key="person_detected",
                track_ids=[track.track_id],
                detection_ids=[],
                window_start=track.first_seen,
                window_end=track.last_seen,
                camera_id=track.camera_id,
                correlation_key=correlation_key(track.camera_id, "person", self._bucket_epoch(track.last_seen)),
                geometry=ctx.geometry,
                alertable=False,
            )

    def _vehicle_event(self, track: TrackUpdate, ctx) -> EventCandidate:
        if ctx.in_restricted:
            return EventCandidate(
                event_type=EventType.RESTRICTED_ZONE_ACTIVITY,
                language_key="restricted_zone_activity",
                track_ids=[track.track_id],
                detection_ids=[],
                window_start=track.first_seen,
                window_end=track.last_seen,
                camera_id=track.camera_id,
                correlation_key=correlation_key(track.camera_id, "restricted", self._bucket_epoch(track.last_seen)),
                geometry=ctx.geometry,
                alertable=True,
                payload={"night": ctx.is_night, "track_id": track.track_id},
            )
        return EventCandidate(
            event_type=EventType.VEHICLE_DETECTED,
            language_key="vehicle_detected",
            track_ids=[track.track_id],
            detection_ids=[],
            window_start=track.first_seen,
            window_end=track.last_seen,
            camera_id=track.camera_id,
            correlation_key=correlation_key(track.camera_id, "vehicle", self._bucket_epoch(track.last_seen)),
            geometry=ctx.geometry,
            alertable=False,
        )

    def _animal_event(self, track: TrackUpdate, ctx) -> EventCandidate:
        return EventCandidate(
            event_type=EventType.ANIMAL_DETECTED,
            language_key="animal_detected",
            track_ids=[track.track_id],
            detection_ids=[],
            window_start=track.first_seen,
            window_end=track.last_seen,
            camera_id=track.camera_id,
            correlation_key=correlation_key(track.camera_id, "animal", self._bucket_epoch(track.last_seen)),
            geometry=ctx.geometry,
            alertable=False,
        )

    def _fire_event(self, track: TrackUpdate, ctx) -> EventCandidate:
        if track.class_name == "fire":
            return EventCandidate(
                event_type=EventType.FIRE_DETECTED,
                language_key="fire_detected",
                track_ids=[track.track_id],
                detection_ids=[],
                window_start=track.first_seen,
                window_end=track.last_seen,
                camera_id=track.camera_id,
                correlation_key=correlation_key(track.camera_id, "fire", self._bucket_epoch(track.last_seen)),
                geometry=ctx.geometry,
                alertable=True,
            )
        return EventCandidate(
            event_type=EventType.SMOKE_DETECTED,
            language_key="smoke_detected",
            track_ids=[track.track_id],
            detection_ids=[],
            window_start=track.first_seen,
            window_end=track.last_seen,
            camera_id=track.camera_id,
            correlation_key=correlation_key(track.camera_id, "smoke", self._bucket_epoch(track.last_seen)),
            geometry=ctx.geometry,
            alertable=True,
        )

    def _suspicious_composite(
        self,
        persons: List[TrackUpdate],
        vehicles: List[TrackUpdate],
        ctx,
    ) -> EventCandidate:
        all_tracks = persons + vehicles
        return EventCandidate(
            event_type=EventType.SUSPICIOUS_ACTIVITY_HIGH_RISK,
            language_key="suspicious_activity_high_risk",
            track_ids=[t.track_id for t in all_tracks],
            detection_ids=[],
            window_start=min(t.first_seen for t in all_tracks),
            window_end=max(t.last_seen for t in all_tracks),
            camera_id=all_tracks[0].camera_id,
            correlation_key=correlation_key(all_tracks[0].camera_id, "suspicious_high", self._bucket_epoch(all_tracks[0].last_seen)),
            geometry=ctx.geometry,
            alertable=True,
            payload={
                "night": ctx.is_night,
                "restricted": ctx.in_restricted,
                "person_count": len(persons),
                "vehicle_count": len(vehicles),
                "track_ids": [t.track_id for t in all_tracks],
            },
        )