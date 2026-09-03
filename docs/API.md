# VANRAKSHA AI — API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/health/live`, `/health/ready`, `/auth/login`) require Bearer token:

```
Authorization: Bearer <access_token>
```

Token obtained via `POST /auth/login`.

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health/live` | Liveness probe (always 200) |
| GET | `/health/ready` | Readiness probe (DB check) |

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Email/password → JWT |
| POST | `/auth/logout` | Clear cookie |
| GET | `/auth/me` | Current user |

## Cameras

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cameras` | List cameras (paginated) |
| POST | `/cameras` | Create camera |
| GET | `/cameras/{id}` | Get camera |
| PATCH | `/cameras/{id}` | Update camera |
| DELETE | `/cameras/{id}` | Soft delete (retired) |
| POST | `/cameras/{id}/sources` | Add source |
| GET | `/cameras/health` | All camera health |
| GET | `/cameras/{id}/preview` | Latest evidence frame |

## Zones & Forests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forests` | List forest areas |
| POST | `/forests` | Create forest |
| GET | `/zones` | List zones (filter `?restricted=true`) |
| POST | `/zones` | Create zone |
| GET | `/zones/{id}` | Get zone |
| PATCH | `/zones/{id}` | Update zone |

## Rangers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rangers` | List rangers |
| POST | `/rangers` | Create ranger |
| GET | `/rangers/{id}` | Get ranger |
| PATCH | `/rangers/{id}` | Update ranger |

## Locations & SOS

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/locations/rangers/{id}/location` | Ingest ranger GPS |
| GET | `/locations/rangers/locations/latest` | Latest per ranger |
| POST | `/sos/rangers/{id}/sos` | Trigger SOS |

## Patrols

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patrols` | List patrols |
| POST | `/patrols` | Start patrol |
| GET | `/patrols/{id}` | Get patrol |
| PATCH | `/patrols/{id}` | Update/end patrol |

## Ingest Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest/jobs` | Start job `{camera_id}` |
| GET | `/ingest/jobs` | List jobs |
| GET | `/ingest/jobs/{id}` | Get job |
| POST | `/ingest/jobs/{id}/stop` | Stop job |

## Detections & Taxonomy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/detections` | List detections (filter: camera_id, class_name, from_ts, to_ts) |
| GET | `/detections/taxonomy` | Class display names |

## Tracks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tracks` | List tracks (filter: camera_id, active) |
| GET | `/tracks/{id}/points` | Track polyline |

## Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List events (filter: camera_id, event_type, alertable, from_ts, to_ts) |

## Risk

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/risk/weights` | Current risk weights |
| GET | `/risk/min-incident-level` | Minimum level for incident creation |
| POST | `/risk/preview` | Dry-run scoring |

## Incidents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/incidents` | List (filter: status, risk_level, camera_id, from_ts, to_ts) |
| GET | `/incidents/{id}` | Detail with events, evidence, factors |
| POST | `/incidents/{id}/transition` | Status transition |
| POST | `/incidents/{id}/assign` | Assign user/ranger |
| POST | `/incidents/{id}/notes` | Add note |
| GET | `/incidents/{id}/history` | Status history |
| POST | `/incidents/{id}/outcome` | Record outcome (CLOSED only) |
| GET | `/incidents/{id}/outcome` | Get outcome |

## Evidence

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/evidence` | List (filter: incident_id, event_id) |
| GET | `/evidence/{id}` | Metadata + disclaimer |
| GET | `/evidence/{id}/file` | JPEG file |

## Wildlife

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wildlife/observations` | List observations |

## Fire

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/fire/events` | List fire/smoke events |
| GET | `/fire/events/{id}/nearby` | Nearby rangers/cameras |

## Dashboard & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/summary` | Overview counts |
| GET | `/analytics/incidents` | Time-series, by type, by level |
| GET | `/incidents/analytics/false-positive-rate` | FP rate |

## Sync (Edge)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sync/batch` | Batch ingest from edge |

## GeoJSON

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/geo/forests` | Forest areas |
| GET | `/geo/zones` | Zones |
| GET | `/geo/cameras` | Cameras |
| GET | `/geo/incidents` | Incidents |
| GET | `/geo/rangers` | Ranger locations |
| GET | `/geo/wildlife` | Observations |
| GET | `/geo/fire` | Fire events |

## WebSocket

| Endpoint | Topics |
|----------|--------|
| `/api/v1/ws?topics=incidents,health,sos,events` | Real-time updates |

## Settings (Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings/{key}` | Get setting |
| PUT | `/settings/{key}` | Update setting |

Keys: `risk_weights`, `night_window`

## Language

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/language` | Full catalog (for frontend copy) |

## Error Format

All errors return:

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable",
  "details": {},
  "request_id": "abc123"
}
```

Codes: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`, `CONFLICT`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `RATE_LIMITED`, `INTERNAL_ERROR`, `SERVICE_UNAVAILABLE`, `WEBCAM_UNAVAILABLE`.