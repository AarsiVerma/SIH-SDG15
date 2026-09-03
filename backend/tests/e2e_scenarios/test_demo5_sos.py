import pytest
pytestmark = pytest.mark.postgres

"""E2E test for Demo 5: Ranger SOS."""
from datetime import datetime
from uuid import uuid4

from app.services.sos_service import trigger_sos
from app.db.session import get_session
from app.models import Ranger, Incident
from app.models.enums import IncidentStatus, RiskLevel
from sqlalchemy import select


@pytest.mark.asyncio
async def test_demo5_ranger_sos():
    """SOS creates CRITICAL incident."""
    async for session in get_session():
        # Get demo ranger
        ranger = await session.execute(
            select(Ranger).where(Ranger.badge_code == "RNG-001")
        )
        ranger = ranger.scalar_one_or_none()
        if not ranger:
            pytest.skip("Demo ranger not seeded")

        incident = await trigger_sos(session, ranger.id)

        assert incident.risk_score == 100
        assert incident.risk_level == RiskLevel.CRITICAL
        assert incident.status == IncidentStatus.NEW
        assert incident.language_key == "ranger_sos"
        assert "SOS" in incident.public_id

        await session.commit()
