"""IncidentManager - upserts incidents from events."""
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Incident, IncidentEvent, IncidentStatusHistory, Event
from app.models.enums import IncidentStatus, RiskLevel
from app.engines.incident_state import validate_transition
from app.core.language import message_for


class IncidentManager:
    """Creates or attaches incidents from alertable events."""

    def __init__(self, incident_min_level: str = "medium"):
        self.min_level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL,
        }
        self.incident_min_level = self.min_level_map.get(incident_min_level, RiskLevel.MEDIUM)

    async def upsert_from_event(
        self,
        db: AsyncSession,
        event: Event,
        risk_score: int,
        risk_level: RiskLevel,
    ) -> Incident:
        """Create or attach incident for an alertable event."""
        # Check if event already linked
        if event.incidents:
            incident = event.incidents[0].incident
            if incident.status not in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
                incident.risk_score = max(incident.risk_score or 0, risk_score)
                incident.risk_level = max(incident.risk_level or RiskLevel.LOW, risk_level, key=lambda x: x.value)
                incident.updated_at = datetime.utcnow()
                await db.commit()
                return incident

        # Check for existing open incident with same correlation family
        family = event.correlation_key.split(":")[1] if ":" in event.correlation_key else "unknown"
        
        # Optimized query: join incidents with their events in single query
        stmt = select(Incident).options(
            selectinload(Incident.events).selectinload(IncidentEvent.event)
        ).where(
            Incident.status.in_([IncidentStatus.NEW, IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING, IncidentStatus.DISPATCHED]),
        ).order_by(Incident.created_at.desc())
        result = await db.execute(stmt)
        open_incidents = result.scalars().all()

        for inc in open_incidents:
            # Check if any linked event has same correlation family
            for ie in inc.events:
                ev = ie.event
                if ev and ev.correlation_key.split(":")[1] == family:
                    inc.risk_score = max(inc.risk_score or 0, risk_score)
                    inc.risk_level = max(inc.risk_level or RiskLevel.LOW, risk_level, key=lambda x: x.value)
                    inc.updated_at = datetime.utcnow()
                    # Link event
                    db.add(IncidentEvent(incident_id=inc.id, event_id=event.id))
                    await db.commit()
                    return inc

        # Create new incident
        if risk_level.value < self.incident_min_level.value:
            return None  # Below threshold

        title_msg = message_for(event.language_key)
        public_id = await self._generate_public_id(db)

        incident = Incident(
            public_id=public_id,
            title=title_msg["title"],
            language_key=event.language_key,
            status=IncidentStatus.NEW,
            risk_score=risk_score,
            risk_level=risk_level,
            location=event.location,
        )
        db.add(incident)
        await db.flush()

        # Link event
        db.add(IncidentEvent(incident_id=incident.id, event_id=event.id))

        # Status history
        db.add(IncidentStatusHistory(
            incident_id=incident.id,
            from_status=None,
            to_status=IncidentStatus.NEW,
            note="Created from event",
        ))

        await db.commit()
        await db.refresh(incident)
        return incident

    async def _generate_public_id(self, db: AsyncSession) -> str:
        year = datetime.utcnow().year
        stmt = select(func.count(Incident.id)).where(
            Incident.public_id.like(f"INC-{year}-%")
        )
        count = (await db.execute(stmt)).scalar_one() or 0
        return f"INC-{year}-{count + 1:04d}"