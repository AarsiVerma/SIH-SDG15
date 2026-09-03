"""SOS service - creates CRITICAL incident."""
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Ranger, Incident, IncidentStatusHistory, Event
from app.models.enums import IncidentStatus, RiskLevel
from app.engines.incident_manager import IncidentManager
from app.core.language import message_for
from app.core.errors import AppError, ErrorCode


async def trigger_sos(
    db: AsyncSession,
    ranger_id: UUID,
) -> Incident:
    """Create CRITICAL incident from ranger SOS."""
    ranger = await db.get(Ranger, ranger_id)
    if not ranger:
        raise AppError(ErrorCode.NOT_FOUND, "Ranger not found")

    # Get ranger's last location
    from sqlalchemy import func as sa_func
    from app.models import RangerLocation
    latest_loc = await db.execute(
        select(RangerLocation)
        .where(RangerLocation.ranger_id == ranger_id)
        .order_by(RangerLocation.captured_at.desc())
    )
    loc = latest_loc.scalars().first()

    location = loc.geom if loc else None
    if not location:
        # Use a default point if no location
        from geoalchemy2 import WKTElement
        location = WKTElement("POINT(0 0)", srid=4326)

    # Get SOS message from catalog
    msg = message_for("ranger_sos")

    incident = Incident(
        public_id=f"SOS-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        title=msg["title"],
        language_key="ranger_sos",
        status=IncidentStatus.NEW,
        risk_score=100,
        risk_level=RiskLevel.CRITICAL,
        location=location,
        resolution_notes=f"SOS triggered by ranger {ranger.badge_code} ({ranger.name})",
    )
    db.add(incident)
    await db.flush()

    # Status history
    db.add(IncidentStatusHistory(
        incident_id=incident.id,
        from_status=None,
        to_status=IncidentStatus.NEW,
        note="SOS activated",
    ))

    await db.commit()
    await db.refresh(incident)

    # Create associated event for correlation
    event = Event(
        camera_id=None,  # SOS not from camera
        event_type="ranger_sos",
        language_key="ranger_sos",
        correlation_key=f"sos:{ranger_id}:{datetime.utcnow().timestamp()}",
        window_start=datetime.utcnow(),
        window_end=datetime.utcnow(),
        location=location,
        risk_score=100,
        risk_level=RiskLevel.CRITICAL,
        alertable=True,
        payload={"ranger_id": str(ranger_id), "badge_code": ranger.badge_code},
    )
    db.add(event)
    await db.commit()

    return incident