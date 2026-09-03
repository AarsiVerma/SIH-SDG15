# Architecture Decision Record — VANRAKSHA AI

Status: **Adopted (binding for MVP)** · Date: 2026-09-02

## Decision

VANRAKSHA AI is a **modular monolith**. One FastAPI process serves HTTP REST,
WebSockets, and in-process background jobs. No microservices, no message broker
required for MVP.

## Approved stack

| Concern | Choice | License note |
|---------|--------|--------------|
| Language | Python 3.11+ / TypeScript | — |
| Backend framework | FastAPI (Pydantic v2) | MIT |
| Frontend | Next.js App Router + TypeScript | MIT |
| UI styling | Tailwind CSS | MIT |
| Database | PostgreSQL 16 + PostGIS 3 | PostgreSQL license / GPL PostGIS |
| ORM / migrations | SQLAlchemy 2.x + Alembic | MIT |
| Detector (default) | ONNX Runtime + YOLOX | Apache-2.0 |
| Tracker | ByteTrack (MIT port, vendored) — IoU fallback | MIT |
| Dummy detector | in-repo | Apache-2.0 equivalent |
| Map | Leaflet + vanilla JS wrapper | BSD-2 (see VR-004 react-leaflet re-check) |
| Realtime | Native WebSockets | — |
| Testing | pytest + pytest-asyncio + Playwright | MIT |
| Containers | Docker Compose | Apache-2.0 |

## Explicitly rejected for MVP

- Kafka / Redis / RabbitMQ — in-process asyncio jobs suffice
- Kubernetes — single-node Compose is enough
- Ultralytics (YOLO) — AGPL; blocked by default unless `allow_agpl` is set (it is not)
- BoxMOT — AGPL
- Paid APIs (Twilio, map tiles, cloud SMS) — not needed
- Micromamba/Conda-based ML packaging — keep pip-only

## Pipeline

```
Source (file/webcam/rtsp)
  → FrameSampler (target FPS)
  → Detector (Dummy | ONNX YOLOX)          → DetectionCandidate
  → Tracker (IoU | ByteTrack MIT)          → TrackUpdate
  → ContextProvider                        → SceneContext (zones, night, rangers)
  → EventEngine + Correlator               → EventCandidate
  → RiskEngine                             → RiskAssessment (factors)
  → IncidentManager                        → Incident
  → EvidenceStore (annotated JPEG + SHA-256)
  → NotificationProvider (WS + log + DB)
```

## Protocol names (binding)

`VideoSource`, `Detector`, `Tracker`, `ContextProvider`, `EventEngine`,
`RiskEngine`, `IncidentManager`, `EvidenceStore`, `NotificationProvider`,
`LocationProvider`, `SensorSource`, `DroneSource`, `CameraHealthMonitor`.

Each protocol is defined at its first TODO and must not be silently changed.

## License-sensitive choices

- **PostGIS is GPL.** Using it keeps the app's runtime free; legal review of
  distribution is documented in `docs/THIRD_PARTY_LICENSES.md`.
- **Ultralytics is AGPL.** Default is YOLOX (Apache-2.0). AGPL is gated by
  `allow_agpl: false`.
- **FFmpeg**: invoked only for decode/encode; license (LGPL/GPL) noted in the
  third-party registry.
- **react-leaflet**: license must be re-verified (may be Hippocratic). If so,
  use vanilla Leaflet.

## AuthZ model (implemented in VR-083/084)

Four roles: `ADMIN`, `FOREST_OFFICER`, `RANGER`, `VIEWER`. Matrix lives in this
file and is enforced via `require_role` in every router.

## Offline edge

MVP edge mode writes serialized DTOs into a SQLite outbox
(`edge/data/outbox.sqlite`) which is flushed to the central sync API. No CRDT.

## MVP performance target

2 FPS at 640px on CPU with Dummy/YOLOX. No GPU required. (See VR-092.)