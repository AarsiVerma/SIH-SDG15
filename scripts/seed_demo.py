#!/usr/bin/env python3
"""Idempotent demo data seed for Vanraksha Demo Reserve.

Creates:
- Forest area polygon
- Restricted zone, corridor zone
- 3 cameras with file sources pointing to samples/videos/
- 2 simulated rangers
- Default admin user (only if DEMO_MODE=true)
- System settings (risk_weights, night window)
"""
import json
import uuid
from datetime import datetime, time

import asyncio
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from geoalchemy2 import WKTElement

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.session import get_session
from app.models import (
    User, ForestArea, Zone, Camera, CameraSource,
    Ranger, SystemSettings,
    UserRole, ZoneType, CameraStatus, SourceType,
)

DEMO_FOREST = {
    "name": "Vanraksha Demo Reserve",
    "geom": "POLYGON((77.0 12.0, 77.5 12.0, 77.5 12.5, 77.0 12.5, 77.0 12.0))",
}

RESTRICTED_ZONE = {
    "name": "Core Protected Zone",
    "zone_type": ZoneType.RESTRICTED,
    "is_restricted": True,
    "geom": "POLYGON((77.1 12.1, 77.4 12.1, 77.4 12.4, 77.1 12.4, 77.1 12.1))",
}

CORRIDOR_ZONE = {
    "name": "Wildlife Corridor",
    "zone_type": ZoneType.CORRIDOR,
    "is_restricted": False,
    "geom": "POLYGON((77.0 12.2, 77.2 12.2, 77.2 12.3, 77.0 12.3, 77.0 12.2))",
}

CAMERAS = [
    {
        "name": "Gate Camera North",
        "code": "CAM-GATE-N",
        "location": "POINT(77.15 12.15)",
        "heading_deg": 0.0,
        "status": CameraStatus.ACTIVE,
        "is_simulated": True,
        "sources": [{"source_type": SourceType.FILE, "uri": "/app/samples/videos/gate_north.mp4"}],
    },
    {
        "name": "Perimeter East",
        "code": "CAM-PERIM-E",
        "location": "POINT(77.35 12.25)",
        "heading_deg": 90.0,
        "status": CameraStatus.ACTIVE,
        "is_simulated": True,
        "sources": [{"source_type": SourceType.FILE, "uri": "/app/samples/videos/perimeter_east.mp4"}],
    },
    {
        "name": "Watchtower South",
        "code": "CAM-WATCH-S",
        "location": "POINT(77.25 12.05)",
        "heading_deg": 180.0,
        "status": CameraStatus.ACTIVE,
        "is_simulated": True,
        "sources": [{"source_type": SourceType.FILE, "uri": "/app/samples/videos/watchtower_south.mp4"}],
    },
]

RANGERS = [
    {"badge_code": "RNG-001", "name": "Ranger Arjun Patel", "is_simulated": True},
    {"badge_code": "RNG-002", "name": "Ranger Priya Sharma", "is_simulated": True},
]

ADMIN_USER = {
    "email": "admin@vanraksha.local",
    "password": "changeme",
    "full_name": "System Administrator",
    "role": UserRole.ADMIN,
}

RISK_WEIGHTS = {
    "max_score": 100,
    "levels": {
        "low": [0, 30],
        "medium": [31, 60],
        "high": [61, 80],
        "critical": [81, 100],
    },
    "factors": [
        {"code": "restricted_zone", "delta": 25},
        {"code": "nighttime", "delta": 10},
        {"code": "vehicle", "delta": 15},
        {"code": "suspicious_pattern", "delta": 25},
        {"code": "wildlife_nearby", "delta": 15},
        {"code": "repeated_movement", "delta": 10},
        {"code": "camera_tampering", "delta": 20},
        {"code": "authorized_ranger", "delta": -40},
    ],
}

NIGHT_SETTINGS = {
    "night_start": "18:00",
    "night_end": "06:00",
    "timezone": "Asia/Kolkata",
}


async def seed_forest_and_zones(session):
    # Forest
    forest_stmt = insert(ForestArea).values(
        id=uuid.uuid4(),
        name=DEMO_FOREST["name"],
        geom=WKTElement(DEMO_FOREST["geom"], srid=4326),
    ).on_conflict_do_nothing(index_elements=["name"])
    await session.execute(forest_stmt)
    await session.flush()

    forest = (await session.execute(
        select(ForestArea).where(ForestArea.name == DEMO_FOREST["name"])
    )).scalar_one()
    forest_id = forest.id

    # Restricted zone
    rz_stmt = insert(Zone).values(
        id=uuid.uuid4(),
        forest_id=forest_id,
        name=RESTRICTED_ZONE["name"],
        zone_type=RESTRICTED_ZONE["zone_type"],
        is_restricted=RESTRICTED_ZONE["is_restricted"],
        geom=WKTElement(RESTRICTED_ZONE["geom"], srid=4326),
    ).on_conflict_do_nothing(index_elements=["forest_id", "name"])
    await session.execute(rz_stmt)

    # Corridor zone
    cz_stmt = insert(Zone).values(
        id=uuid.uuid4(),
        forest_id=forest_id,
        name=CORRIDOR_ZONE["name"],
        zone_type=CORRIDOR_ZONE["zone_type"],
        is_restricted=CORRIDOR_ZONE["is_restricted"],
        geom=WKTElement(CORRIDOR_ZONE["geom"], srid=4326),
    ).on_conflict_do_nothing(index_elements=["forest_id", "name"])
    await session.execute(cz_stmt)

    await session.flush()
    return forest_id


async def seed_cameras(session, forest_id):
    for cam_data in CAMERAS:
        cam_stmt = insert(Camera).values(
            id=uuid.uuid4(),
            forest_id=forest_id,
            name=cam_data["name"],
            code=cam_data["code"],
            location=WKTElement(cam_data["location"], srid=4326),
            heading_deg=cam_data["heading_deg"],
            status=cam_data["status"],
            is_simulated=cam_data["is_simulated"],
        ).on_conflict_do_nothing(index_elements=["code"])
        await session.execute(cam_stmt)
        await session.flush()

        camera = (await session.execute(
            select(Camera).where(Camera.code == cam_data["code"])
        )).scalar_one()

        for src in cam_data["sources"]:
            src_stmt = insert(CameraSource).values(
                id=uuid.uuid4(),
                camera_id=camera.id,
                source_type=src["source_type"],
                uri=src["uri"],
                extra={},
            ).on_conflict_do_nothing(index_elements=["camera_id", "uri"])
            await session.execute(src_stmt)


async def seed_rangers(session):
    for r in RANGERS:
        stmt = insert(Ranger).values(
            id=uuid.uuid4(),
            badge_code=r["badge_code"],
            name=r["name"],
            is_simulated=r["is_simulated"],
            active=True,
        ).on_conflict_do_nothing(index_elements=["badge_code"])
        await session.execute(stmt)


async def seed_admin_user(session):
    settings = get_settings()
    if not settings.demo_mode:
        return

    stmt = insert(User).values(
        id=uuid.uuid4(),
        email=ADMIN_USER["email"],
        hashed_password=get_password_hash(ADMIN_USER["password"]),
        full_name=ADMIN_USER["full_name"],
        role=ADMIN_USER["role"],
        is_active=True,
    ).on_conflict_do_nothing(index_elements=["email"])
    await session.execute(stmt)


async def seed_system_settings(session):
    # Risk weights
    rw_stmt = insert(SystemSettings).values(
        key="risk_weights",
        value=RISK_WEIGHTS,
    ).on_conflict_do_update(index_elements=["key"], set_={"value": RISK_WEIGHTS})
    await session.execute(rw_stmt)

    # Night window (stored in separate key for clarity)
    night_stmt = insert(SystemSettings).values(
        key="night_window",
        value=NIGHT_SETTINGS,
    ).on_conflict_do_update(index_elements=["key"], set_={"value": NIGHT_SETTINGS})
    await session.execute(night_stmt)


async def main():
    print("Seeding demo data...")
    async for session in get_session():
        await seed_forest_and_zones(session)
        forest = (await session.execute(
            select(ForestArea).where(ForestArea.name == DEMO_FOREST["name"])
        )).scalar_one()
        await seed_cameras(session, forest.id)
        await seed_rangers(session)
        await seed_admin_user(session)
        await seed_system_settings(session)
        await session.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())