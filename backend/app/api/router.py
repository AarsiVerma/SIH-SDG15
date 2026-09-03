"""API router v1 — aggregate all endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import (
    health, cameras, zones, rangers, settings, ingest, detections, tracks, events, risk, incidents, evidence,
    wildlife, fire, locations, sos, patrols, ws, geo, dashboard, auth, sync, outcomes, metrics, language
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health")
api_router.include_router(cameras.router, prefix="/cameras")
api_router.include_router(zones.router, prefix="/zones")
api_router.include_router(zones.forests_router)
api_router.include_router(rangers.router, prefix="/rangers")
api_router.include_router(settings.router, prefix="/settings")
api_router.include_router(ingest.router, prefix="/ingest")
api_router.include_router(detections.router, prefix="/detections")
api_router.include_router(tracks.router, prefix="/tracks")
api_router.include_router(events.router, prefix="/events")
api_router.include_router(risk.router, prefix="/risk")
api_router.include_router(incidents.router, prefix="/incidents")
api_router.include_router(evidence.router, prefix="/evidence")
api_router.include_router(wildlife.router, prefix="/wildlife")
api_router.include_router(fire.router, prefix="/fire")
api_router.include_router(locations.router, prefix="/locations")
api_router.include_router(sos.router, prefix="/sos")
api_router.include_router(patrols.router, prefix="/patrols")
api_router.include_router(ws.router, prefix="/ws")
api_router.include_router(geo.router, prefix="/geo")
api_router.include_router(dashboard.router)
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(sync.router, prefix="/sync")
api_router.include_router(outcomes.router, prefix="/incidents")
api_router.include_router(metrics.router, prefix="/metrics")
api_router.include_router(language.router, prefix="/language")


# TODO(auth VR-083): attach require_role to protected routers as they land.