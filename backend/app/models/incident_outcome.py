"""Incident outcome model (VR-089)."""
import uuid
import enum
from datetime import datetime

from sqlalchemy import DateTime, String, ForeignKey, Enum, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IncidentOutcome(str, enum.Enum):
    CONFIRMED_ISSUE = "confirmed_issue"
    FALSE_POSITIVE = "false_positive"
    DUPLICATE = "duplicate"
    TRAINING = "training"
    OTHER = "other"


class IncidentOutcomeRecord(Base):
    __tablename__ = "incident_outcomes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    outcome: Mapped[IncidentOutcome] = mapped_column(Enum(IncidentOutcome), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)