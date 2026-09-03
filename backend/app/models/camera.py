"""Camera and CameraSource models."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Boolean, ForeignKey, Float, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base
from app.models.enums import CameraStatus, SourceType


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    forest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("forest_areas.id", ondelete="SET NULL"), nullable=True)
    location: Mapped[bytes] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    heading_deg: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[CameraStatus] = mapped_column(String(32), nullable=False, default=CameraStatus.PLANNED)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    forest = relationship("ForestArea", back_populates="cameras", lazy="selectin")
    sources = relationship("CameraSource", back_populates="camera", lazy="selectin", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_cameras_location", "location", postgresql_using="gist"),)


class CameraSource(Base):
    __tablename__ = "camera_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(String(32), nullable=False)
    uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    extra: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    camera = relationship("Camera", back_populates="sources", lazy="selectin")