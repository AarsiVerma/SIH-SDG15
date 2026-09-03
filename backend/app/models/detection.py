"""Detection model."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Integer, Float, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.db.base import Base


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True)
    frame_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    class_name: Mapped[str] = mapped_column(String(64), nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_xyxy: Mapped[dict] = mapped_column(JSON, nullable=False)
    centroid: Mapped[bytes | None] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    track_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True, index=True)
    detector_id: Mapped[str] = mapped_column(String(64), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_detections_camera_time", "camera_id", "captured_at"),
        Index("ix_detections_centroid", "centroid", postgresql_using="gist"),
    )