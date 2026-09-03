"""GeoJSON API endpoints."""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2 import functions as geofunc
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models import (
    ForestArea, Zone, Camera, Incident, Event,
    Ranger, RangerLocation, WildlifeObservation
)
from app.models.enums import EventType
from app.schemas.geo import FeatureCollection, Feature, Geometry

router = APIRouter(prefix="/geo", tags=["geo"])


def _to_feature(model_obj, properties: dict, geom_attr: str = "geom") -> Feature:
    geom = getattr(model_obj, geom_attr, None)
    if geom:
        shape = to_shape(geom)
        return Feature(
            geometry=Geometry(
                type=shape.geom_type,
                coordinates=list(shape.coords) if shape.geom_type == "Point" else [list(shape.exterior.coords)],
            ),
            properties=properties,
        )
    return Feature(geometry=None, properties=properties)


@router.get("/forests", response_model=FeatureCollection)
async def geo_forests(db: AsyncSession = Depends(get_db)):
    stmt = select(ForestArea)
    result = await db.execute(stmt)
    features = [
        _to_feature(f, {"id": str(f.id), "name": f.name})
        for f in result.scalars().all()
    ]
    return FeatureCollection(features=features)


@router.get("/zones", response_model=FeatureCollection)
async def geo_zones(
    restricted: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Zone)
    if restricted is not None:
        stmt = stmt.where(Zone.is_restricted == restricted)
    result = await db.execute(stmt)
    features = [
        _to_feature(z, {"id": str(z.id), "name": z.name, "type": z.zone_type, "is_restricted": z.is_restricted})
        for z in result.scalars().all()
    ]
    return FeatureCollection(features=features)


@router.get("/cameras", response_model=FeatureCollection)
async def geo_cameras(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Camera)
    if status:
        stmt = stmt.where(Camera.status == status)
    result = await db.execute(stmt)
    features = [
        _to_feature(c, {"id": str(c.id), "code": c.code, "name": c.name, "status": c.status})
        for c in result.scalars().all()
    ]
    return FeatureCollection(features=features)


@router.get("/incidents", response_model=FeatureCollection)
async def geo_incidents(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Incident)
    if status:
        stmt = stmt.where(Incident.status == status)
    if risk_level:
        stmt = stmt.where(Incident.risk_level == risk_level)
    result = await db.execute(stmt)
    features = [
        _to_feature(i, {
            "id": str(i.id),
            "public_id": i.public_id,
            "title": i.title,
            "status": i.status,
            "risk_level": i.risk_level,
        })
        for i in result.scalars().all()
    ]
    return FeatureCollection(features=features)


@router.get("/rangers", response_model=FeatureCollection)
async def geo_rangers(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    from app.models import RangerLocation
    stmt = select(RangerLocation).order_by(
        RangerLocation.ranger_id, RangerLocation.captured_at.desc()
    )
    result = await db.execute(stmt)
    # Distinct by ranger_id
    seen = set()
    features = []
    for loc in result.scalars().all():
        if loc.ranger_id in seen:
            continue
        seen.add(loc.ranger_id)
        features.append(_to_feature(loc, {
            "ranger_id": str(loc.ranger_id),
            "captured_at": loc.captured_at.isoformat(),
        }, geom_attr="geom"))
    return FeatureCollection(features=features)


@router.get("/wildlife", response_model=FeatureCollection)
async def geo_wildlife(
    camera_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(WildlifeObservation)
    if camera_id:
        stmt = stmt.where(WildlifeObservation.camera_id == camera_id)
    result = await db.execute(stmt)
    features = [
        _to_feature(w, {
            "id": str(w.id),
            "species": w.species,
            "count": w.count_estimate,
        })
        for w in result.scalars().all()
    ]
    return FeatureCollection(features=features)


@router.get("/fire", response_model=FeatureCollection)
async def geo_fire(
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event).where(Event.event_type.in_(["fire_detected", "smoke_detected"]))
    result = await db.execute(stmt)
    features = [
        _to_feature(e, {
            "id": str(e.id),
            "event_type": e.event_type,
            "severity": e.payload.get("severity", "unknown"),
        })
        for e in result.scalars().all()
    ]
    return FeatureCollection(features=features)