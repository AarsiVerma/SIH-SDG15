"""Track and TrackPoint models."""
import uuid
import enum
from datetime import datetime

from sqlalchemy import DateTime, String, Integer, Float, ForeignKey, JSON, Index, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from app.db.base import Base


class TrackStatus(str, enum.Enum):
    ACTIVE = "active"
    ENDED = "ended"


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    local_track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_name: Mapped[str] = mapped_column(String(64), nullable=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[TrackStatus] = mapped_column(SAEnum(TrackStatus), nullable=False, default=TrackStatus.ACTIVE)
    global_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)  # Future ReID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    points = relationship("TrackPoint", back_populates="track", lazy="selectin", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tracks_camera_time", "camera_id", "first_seen"),
        Index("ix_tracks_local", "camera_id", "local_track_id", unique=True),
    )


class TrackPoint(Base):
    __tablename__ = "track_points"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    bbox_xyxy: Mapped[dict] = mapped_column(JSON, nullable=False)
    centroid_image: Mapped[dict] = mapped_column(JSON, nullable=False)
    map_point: Mapped[bytes | None] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)

    track = relationship("Track", back_populates="points", lazy="selectin")

    __table_args__ = (
        Index("ix_track_points_track_time", "track_id", "captured_at"),
        Index("ix_track_points_map", "map_point", postgresql_using="gist"),
    )