"""Forest area model."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class ForestArea(Base):
    __tablename__ = "forest_areas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    geom: Mapped[bytes] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    zones = relationship("Zone", back_populates="forest", lazy="selectin")
    cameras = relationship("Camera", back_populates="forest", lazy="selectin")

    __table_args__ = (Index("ix_forest_areas_geom", "geom", postgresql_using="gist"),)