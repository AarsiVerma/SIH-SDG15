"""Zone model."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base
from app.models.enums import ZoneType


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("forest_areas.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone_type: Mapped[ZoneType] = mapped_column(String(32), nullable=False, default=ZoneType.OTHER)
    is_restricted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    geom: Mapped[bytes] = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    forest = relationship("ForestArea", back_populates="zones", lazy="selectin")

    __table_args__ = (Index("ix_zones_geom", "geom", postgresql_using="gist"),)