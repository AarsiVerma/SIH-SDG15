"""Dashboard summary API."""
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.session import get_db
from app.models import Incident, Camera, CameraHealth, Ranger
from app.models.enums import IncidentStatus, CameraHealthState, RiskLevel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    # Open incidents
    open_statuses = [
        IncidentStatus.NEW,
        IncidentStatus.ACKNOWLEDGED,
        IncidentStatus.INVESTIGATING,
        IncidentStatus.DISPATCHED,
    ]
    open_stmt = select(func.count(Incident.id)).where(Incident.status.in_(open_statuses))
    open_count = (await db.execute(open_stmt)).scalar_one()

    # By level
    level_counts = {}
    for level in RiskLevel:
        stmt = select(func.count(Incident.id)).where(
            Incident.status.in_(open_statuses),
            Incident.risk_level == level,
        )
        level_counts[level.value] = (await db.execute(stmt)).scalar_one()

    # Cameras
    total_cams = (await db.execute(select(func.count(Camera.id)))).scalar_one()
    online_cams = (await db.execute(
        select(func.count(CameraHealth.id)).where(CameraHealth.state == CameraHealthState.ONLINE)
    )).scalar_one()

    # Rangers
    active_rangers = (await db.execute(
        select(func.count(Ranger.id)).where(Ranger.active == True)
    )).scalar_one()

    # Last SOS
    from app.models import Event
    sos_stmt = select(Event).where(Event.event_type == "ranger_sos").order_by(Event.created_at.desc()).limit(1)
    last_sos = (await db.execute(sos_stmt)).scalar_one_or_none()

    return {
        "open_incidents": open_count,
        "incidents_by_level": level_counts,
        "cameras_online": online_cams,
        "cameras_total": total_cams,
        "rangers_active": active_rangers,
        "last_sos_at": last_sos.created_at.isoformat() if last_sos else None,
    }