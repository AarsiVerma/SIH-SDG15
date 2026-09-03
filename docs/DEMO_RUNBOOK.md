# VANRAKSHA AI — SIH Demo Runbook

## Overview

Seven scripted demos covering the full DETECT → CORRELATE → ASSESS → RESPOND pipeline.
All demos run on file video with DummyDetector — no GPU or live cameras required.

## Prerequisites

```bash
# Start stack
docker compose up -d

# Run migrations
docker compose run --rm api alembic -c backend/alembic.ini upgrade head

# Seed demo data
docker compose run --rm api python scripts/seed_demo.py
```

## Demo 1 — Suspicious Activity (Correlation)

**Scenario**: Person + vehicle in restricted zone at night → single HIGH incident.

**Setup**:
- Camera `CAM-GATE-N` in restricted zone
- Dummy script: frames 10-50 person, 60-80 vehicle
- Time: 22:00 (night)

**Run**:
```bash
docker compose run --rm api python -m app.demo.scripts.demo_suspicious
```

**Expected**:
- One incident `INC-2026-XXXX` status NEW, risk HIGH
- Factors: restricted_zone(+25), nighttime(+10), vehicle(+15), suspicious_pattern(+25) = 75
- Evidence JPEG with bboxes
- WebSocket push to Command Centre

**Say aloud**: *"High-risk suspicious activity detected. Ranger verification required."*

---

## Demo 2 — Wildlife Observation

**Scenario**: Animal track triggers wildlife observation (no incident).

**Setup**:
- Camera `CAM-PERIM-E` in corridor zone
- Dummy script: frames 20-60 animal class
- Time: 14:00 (day)

**Run**:
```bash
docker compose run --rm api python -m app.demo.scripts.demo_wildlife
```

**Expected**:
- Wildlife observation created (species: unknown)
- No incident (below MEDIUM threshold)
- Map shows animal icon in corridor

**Say aloud**: *"Animal detected (species unverified). Unusual movement detected; ranger verification recommended."*

---

## Demo 3 — Fire Detection (Stub)

**Scenario**: Smoke/fire detection creates HIGH incident.

**Setup**:
- Camera `CAM-WATCH-S` 
- Dummy script: frames 30-40 fire class
- Time: 15:00

**Run**:
```bash
docker compose run --rm api python -m app.demo.scripts.demo_fire
```

**Expected**:
- Fire incident created, risk HIGH (conf > 0.7)
- Nearby rangers listed
- Spread prediction: null (MVP)

**Say aloud**: *"Possible fire detected. Ranger verification required. No spread model in MVP."*

---

## Demo 4 — Camera Failure

**Scenario**: Camera goes offline → DEGRADED health, no false incident.

**Setup**:
- Camera `CAM-GATE-N` running
- Stop worker: `docker compose stop worker`

**Run**:
```bash
# Wait 35 seconds (offline_after=30)
# Then check health
curl http://localhost:8000/api/v1/cameras/health
```

**Expected**:
- Camera health: OFFLINE, reason `pipeline_stall`
- No incident created (empty scene ≠ failure)
- Health page shows "pipeline_stall"

**Say aloud**: *"Camera failure suspected. Verification required. No alert — empty scene is not failure."*

---

## Demo 5 — Ranger SOS

**Scenario**: Ranger triggers SOS → CRITICAL incident.

**Setup**:
- Ranger `RNG-001` exists
- Last location near `CAM-GATE-N`

**Run**:
```bash
curl -X POST http://localhost:8000/api/v1/sos/rangers/<ranger-id>/sos \
  -H "Authorization: Bearer <token>"
```

**Expected**:
- Incident created: CRITICAL, status NEW
- Public ID: `SOS-20260902-...`
- Language: "Ranger emergency signal"
- Immediate WebSocket push

**Say aloud**: *"Ranger emergency signal. Immediate verification required."*

---

## Demo 6 — Correlation (One Incident, Not Five)

**Scenario**: Same as Demo 1 but verify single incident.

**Setup**: Same as Demo 1

**Run**:
```bash
docker compose run --rm api python -m app.demo.scripts.demo_correlation
```

**Expected**:
- Only ONE incident created
- Events: person + vehicle + restricted + night merged
- Event factors show all 4 contributors
- Incident public_id same across retries

**Say aloud**: *"Correlation engine merged 5 signals into 1 incident. No duplicate alerts."*

---

## Demo 7 — Offline Sync

**Scenario**: Edge collects offline, syncs when online.

**Setup**:
- `SYNC_URL=""` (offline)
- Run edge worker
- Then `SYNC_URL="http://api:8000"` and flush

**Run**:
```bash
python scripts/demo_offline_sync.py
```

**Expected**:
- 3 detections queued in local outbox
- After flush: incidents appear in central DB
- Idempotency: re-flush creates no duplicates

**Say aloud**: *"Offline-first: data queued locally, synced when connection restored. Zero duplicates."*

---

## Common Commands

```bash
# View incidents
curl http://localhost:8000/api/v1/incidents | jq

# View evidence
curl http://localhost:8000/api/v1/evidence | jq

# View camera health
curl http://localhost:8000/api/v1/cameras/health | jq

# Check logs
docker compose logs -f api
docker compose logs -f worker
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| DB connection refused | `docker compose up -d db` wait for healthy |
| Migrations fail | Check `alembic.ini` path, run from backend dir |
| No incidents created | Check `incident_min_level` in settings, verify event.alertable=true |
| WebSocket not connecting | Check `/api/v1/ws` endpoint, CORS |
| Evidence 404 | Run `python scripts/seed_demo.py` to create cameras |

## Attribution

Sample videos: Use CC0/CC-BY licensed wildlife footage from:
- https://www.pexels.com/search/wildlife/
- https://www.videvo.net/
- Custom synthetic videos via `scripts/download_models.py` (generates test MP4s)

**Never use real poaching footage or identifiable persons without rights.**