# VANRAKSHA AI — COMPLETE IMPLEMENTATION ROADMAP

**Status:** Engineering master plan (planning only; no production implementation in this document’s authoring pass).  
**Audience:** OpenCode / any implementation agent executing **one TODO at a time**.  
**Companion:** `docs/TODOS.md` (atomic tasks VR-001 … VR-096).  
**Product:** AI-Powered Forest Intelligence & Early Warning System — “From Detection to Decision”.

---

## 1. Current Repository Audit

### 1.1 Inspection performed

Workspace path inspected: `R:\VANRAKSHA-AI`.

Commands/tools used:

- Recursive glob of the workspace (`**/*`)
- Directory listing including hidden entries (`dir /a`, `Get-ChildItem -Force`)
- Git detection (`git status`, `git rev-parse --is-inside-work-tree`)

### 1.2 What exists (factual)

| Item | Result |
|------|--------|
| Files | **0 files** |
| Subdirectories (other than `.` / `..`) | **none** |
| Git repository | **No.** `fatal: not a git repository` |
| README, package manifests, Docker files, source | **Do not exist** |
| Existing frameworks to reuse | **None** |
| Existing models, datasets, sample videos | **None** |
| Existing CI | **None** |

This is a **greenfield empty folder**, not an incomplete app. Do not invent files, “existing Next.js apps”, or prior Python packages.

### 1.3 What can be reused

Nothing in-repo. Reuse is limited to **chosen open-source dependencies** listed in Section 9.

### 1.4 Missing pieces

Everything: VCS, licenses, backend, frontend, database, AI pipeline, GIS, auth, tests, demos, deployment.

### 1.5 Architectural problems / technical debt

None in code (there is no code). The **planning risks** if an agent starts coding without this roadmap:

- Coupling to Ultralytics (AGPL-3.0) without a license gate
- Coupling to a vendor camera SDK
- Cloud-only design that fails in forests
- “Poacher detected” wording
- Microservices / Kafka / K8s before a working monolith
- Training custom models before a pretrained MVP works

### 1.6 Audit conclusion

**PHASE 0 is complete as an inspection.** Implementation starts at **VR-001** (git + ignore rules) on empty disk. Stack is a **recommendation**, not an inherited constraint.

---

## 2. Target Architecture

### 2.1 Style

**Modular monolith** in one Git repository.

- One FastAPI process for HTTP + WebSockets (MVP).
- One pipeline worker process that **imports the same Python package** (ingestion → detect → track → events → risk → incidents → evidence).
- One Next.js Command Centre.
- One PostgreSQL + PostGIS database.
- An **edge worker** that is the same pipeline with a local SQLite/outbox and a sync client. MVP may run the edge worker on the same machine with `SYNC_MODE=offline` to simulate disconnect.

Do **not** introduce Kafka, Redis, Kubernetes, or extra microservices for MVP.

Optional later (ADVANCED/FUTURE, not MVP): Redis for WS fan-out, object storage for evidence, message broker.

### 2.2 Component responsibilities

| Component | Responsibility |
|-----------|----------------|
| `VideoSource` | Produce `Frame` objects. No AI. |
| `FrameSampler` | Drop/keep frames by FPS / motion / wall-clock. |
| `Detector` | Frame → `list[DetectionCandidate]` (class, bbox, confidence). No incidents. |
| `Tracker` | Detections + frame → `list[TrackUpdate]` with stable `track_id`. |
| `ContextProvider` | Location + time + camera → zones, night/day, nearby rangers/wildlife. |
| `EventEngine` | Tracks + context → `EventCandidate[]` with correlation keys. |
| `RiskEngine` | Event + configurable factors → score, level, **factor breakdown**. |
| `IncidentManager` | Group events → incident lifecycle. |
| `EvidenceStore` | Persist hashed frames/clips + metadata. Not “legal-grade”. |
| `NotificationProvider` | In-app + WebSocket. Optional email/SMS later. |
| `LocationProvider` | Ranger positions (simulated GPS in MVP). |
| `SensorSource` / `DroneSource` | Interfaces + stubs only until FUTURE phase. |
| `CameraHealthMonitor` | Heartbeats, stall vs empty scene, tamper heuristics. |
| API | Authz, validation, CRUD, pipeline control. |
| Command Centre | Forest operations UI, not a generic admin theme. |

### 2.3 AI pipeline and data contracts

```
VideoSource.read_frame()
  → Frame { camera_id, source_id, captured_at, seq, image_bgr, width, height }

FrameSampler.should_process(Frame)
  → Frame | skip

Detector.detect(Frame)
  → DetectionCandidate[] {
      class_id, class_name, confidence, bbox_xyxy, detector_id, model_version
    }

Tracker.update(Frame, DetectionCandidate[])
  → TrackUpdate[] {
      track_id, class_name, confidence, bbox_xyxy, centroid, first_seen, last_seen
    }

ContextProvider.for_track(TrackUpdate, Frame)
  → SceneContext {
      zone_ids[], in_restricted, is_night, nearby_ranger_ids[], nearby_wildlife_track_ids[],
      camera_health_ok
    }

EventEngine.evaluate(window of TrackUpdate + SceneContext)
  → EventCandidate[] {
      event_type, language_key, related_track_ids, related_detection_ids,
      time_window, geometry, correlation_key
    }

RiskEngine.score(EventCandidate, SceneContext, settings)
  → RiskAssessment {
      score: 0-100, level, factors: [{code, delta, reason}],
      requires_human_verification: true
    }

IncidentManager.upsert(EventCandidate[], RiskAssessment)
  → Incident { status=NEW, ... }

EvidenceStore.capture(Frame, TrackUpdate, Incident)
  → EvidenceRef { sha256, path, kind=frame|clip }

NotificationProvider.publish(IncidentAlert)
  → WebSocket topic `incidents` + persist Alert
```

**Layer distinction (must not collapse):**

| Layer | What it is | What it is not |
|-------|------------|----------------|
| Detection | “person bbox conf 0.81” | Not a crime |
| Track | Same object over time | Not intent |
| Event | Pattern in a window | Not a legal finding |
| Risk | Configurable score + reasons | Not certainty |
| Incident | Operational case for humans | Not an accusation |
| Verification | Ranger/officer status change | AI never auto-closes HIGH/CRITICAL without policy |

**Required UI/API language:** never “Poacher detected.” Use catalog strings, e.g. `suspicious_activity_high_risk` → “High-risk suspicious activity detected. Ranger verification required.”

### 2.4 Backend flow

HTTP clients → FastAPI routers → Pydantic schemas → services → SQLAlchemy models → PostgreSQL/PostGIS.  
Pipeline worker uses the same services; does not call HTTP itself for the hot path.

### 2.5 Frontend flow

Next.js App Router → typed API client → React Query (or SWR) for REST; native WebSocket for live incidents/health. Leaflet map layers subscribe to GeoJSON + WS patches.

### 2.6 Database flow

Alembic migrations only. Spatial columns via PostGIS `geometry(Point,4326)` / `geometry(Polygon,4326)`. GIST indexes on all geometries. Application never stores WKT in unstructured text as the source of truth.

### 2.7 Offline / sync architecture (MVP simulated)

```
EDGE NODE (same codebase, EDGE_MODE=true)
  local pipeline → local detections/events/incidents (UUIDs)
  → sync_outbox (JSON payloads, idempotency_key)
  → when online: POST /api/v1/sync/batch

CENTRAL
  upsert by idempotency_key
  reject/merge duplicates (same camera_id + captured_at + track_id + event_type)
```

No real ruggedized hardware required.

---

## 3. Target Repository Structure

Only paths justified by the architecture:

```
VANRAKSHA-AI/
  README.md
  LICENSE                    # project license TBD in VR-004 (recommend MIT for app code)
  .gitignore
  .env.example
  docker-compose.yml
  docker-compose.prod.yml    # PHASE 27
  Makefile                   # or scripts/dev.ps1 on Windows
  pyproject.toml             # backend + pipeline workspace
  docs/
    IMPLEMENTATION_ROADMAP.md
    TODOS.md
    ARCHITECTURE.md
    LANGUAGE.md              # detection vs inference vs risk vs verification
    THIRD_PARTY_LICENSES.md
    THREAT_MODEL.md
    DEMO_RUNBOOK.md
    API.md                   # optional; OpenAPI is source of truth
  backend/
    Dockerfile
    alembic.ini
    alembic/versions/
    app/
      __init__.py
      main.py
      core/                  # config, logging, security, rbac
      db/                    # session, base
      models/
      schemas/
      api/v1/                # routers
      services/
      engines/               # event, risk, incident, correlation
      pipeline/              # orchestrator
      sources/               # video, location, sensor, drone stubs
      vision/                # detector, tracker adapters
      evidence/
      sync/
      ws/
      notifications/
    tests/
  frontend/
    Dockerfile
    package.json
    src/app/                 # Next.js App Router
    src/components/
    src/lib/                 # api client, ws, geo
    src/types/
    e2e/                     # Playwright
  edge/
    README.md
    worker.py                # thin entry; imports backend.app.pipeline
  samples/
    README.md                # how to obtain demo MP4s (do not commit huge binaries)
    videos/.gitkeep
    geo/                     # demo forest GeoJSON
  models/
    README.md                # download scripts; weights gitignored
    .gitkeep
  scripts/
    download_models.py
    seed_demo.py
```

Do not add `k8s/`, `kafka/`, or extra `services/camera-ms` directories for MVP.

---

## 4–5. COMPLETE TODO ROADMAP

All atomic tasks live in **`docs/TODOS.md`**. IDs **VR-001 … VR-096**. Each uses the required template (OBJECTIVE, FILES, IMPLEMENTATION, INTERFACES, DEPENDENCIES, INPUTS, OUTPUTS, ACCEPTANCE CRITERIA, TESTS, DO NOT).

Phase map:

| Phase | TODOs | Intent |
|-------|-------|--------|
| 0 Audit & architecture docs | VR-001–VR-004 | Git, language, ADR, licenses |
| 1 Foundation | VR-005–VR-011 | Python, FastAPI, Next.js, Docker, config, logs |
| 2 Infrastructure & DB | VR-012–VR-019 | Alembic + full MVP schema + seed |
| 3 Backend core | VR-020–VR-024 | Errors, pagination, camera/zone/forest APIs |
| 4 Video ingestion | VR-025–VR-029 | VideoSource, file/webcam/RTSP, sampler, jobs |
| 5 Detection | VR-030–VR-034 | Detector, dummy, ONNX, persist, API, taxonomy |
| 6 Tracking | VR-035–VR-038 | Tracker, IoU, ByteTrack, persist/API |
| 7 Context & GIS data | VR-039–VR-041 | ContextProvider, zones, time, proximity |
| 8 Event engine | VR-042–VR-045 | Types, engine, correlation, API |
| 9 Risk engine | VR-046–VR-048 | Config, scoring, API |
| 10 Incidents | VR-049–VR-052 | State machine, manager, API, audit |
| 11 Evidence | VR-053–VR-055 | Store, capture, API |
| 12 Wildlife | VR-056–VR-058 | Observations, classifier protocol, anomaly |
| 13 Fire | VR-059–VR-060 | Mapping, severity, API |
| 14 Ranger safety | VR-061–VR-063 | GPS, SOS, patrols, inactivity stub |
| 15 Camera health | VR-064–VR-066 | Heartbeat, stall vs empty, tamper MVP |
| 16 Real-time | VR-067–VR-068 | WS hub + domain publish |
| 17 GIS APIs + map | VR-069–VR-071 | GeoJSON, Leaflet, layers |
| 18 Command Centre | VR-072–VR-082 | Shell through analytics |
| 19 AuthZ | VR-083–VR-085 | JWT, RBAC, UI guards |
| 20 Offline sync | VR-086–VR-088 | Edge, outbox, sync API, simulator |
| 21 Analytics | VR-089 | Stats + outcome counters |
| 22 Testing extras | VR-090 | Full E2E scenario pack |
| 23 Security | VR-091 | Hardening + threat model |
| 24 Performance | VR-092 | Sampling, indexes, metrics |
| 25 Demos | VR-093 | Samples + runbook |
| 26 Documentation | VR-094 | Operator README / OpenAPI polish |
| 27 Deployment | VR-095 | Prod compose + backups |
| 28 Future hardware prep | VR-096 | Sensor/drone/location stubs + model versioning |

---

## 6. DEPENDENCY GRAPH

Critical path (cannot skip):

```
VR-001 → VR-002 → VR-003 → VR-004
    → VR-005 → VR-006 → VR-007 → VR-008
    → VR-010 (compose; can parallel VR-009 frontend skeleton)
    → VR-012 → VR-013 → VR-014 … → VR-019
    → VR-020 → VR-021 → VR-022
    → VR-025 → VR-026 → VR-028 → VR-029
    → VR-030 → VR-031 → VR-032 → VR-033
    → VR-035 → VR-036 → VR-037
    → VR-039 → VR-042 → VR-043 → VR-044
    → VR-046 → VR-047
    → VR-049 → VR-050
    → VR-053 → VR-054
    → VR-067
    → VR-072 … UI
    → VR-083 (auth can start after VR-020; must land before SIH demo)
    → VR-086 → VR-087
    → VR-090 → VR-093 → VR-095
```

**Parallel tracks** (after VR-011 / VR-019 as noted):

| Track | TODOs | After |
|-------|-------|--------|
| Frontend skeleton | VR-009, VR-072 | VR-005 or independently after VR-001 |
| GIS seed + map | VR-069–VR-071 | VR-019 + VR-009 |
| Wildlife / fire / ranger / health | VR-056–VR-066 | VR-045 / VR-052 as listed in each TODO |
| Auth | VR-083–VR-085 | VR-020; tighten routers incrementally |
| Offline | VR-086–VR-088 | VR-050 + VR-033 |
| Docs/licenses | VR-004, VR-094 | early and late |

---

## 7. IMPLEMENTATION ORDER

OpenCode should execute in this order (merge parallel only when staffed with two agents):

1. VR-001 … VR-011 foundation  
2. VR-012 … VR-019 database  
3. VR-020 … VR-024 CRUD APIs  
4. VR-025 … VR-038 video + detect + track  
5. VR-039 … VR-055 context → event → risk → incident → evidence  
6. VR-056 … VR-066 wildlife, fire, ranger, health  
7. VR-067 … VR-068 websockets  
8. VR-069 … VR-082 GIS + Command Centre  
9. VR-083 … VR-085 auth  
10. VR-086 … VR-089 offline + analytics  
11. VR-090 … VR-096 tests, security, perf, demos, docs, deploy, future stubs  

If a single agent: **do not start Command Centre pixels before VR-052** (incident API). Map can start at VR-069 once zones exist.

---

## 8. MVP vs ADVANCED vs FUTURE

| Capability | Class | Notes |
|------------|-------|--------|
| File MP4 + webcam ingestion | **MVP** | |
| RTSP abstraction with optional live | **MVP** (live optional) | Stub allowed if no camera |
| ONNX object detection (person, vehicle, animal, fire/smoke if model supports) | **MVP** | Pretrained; no training |
| DummyDetector | **MVP** | Tests/demos without GPU |
| Persistent tracking (IoU + ByteTrack MIT) | **MVP** | |
| Cross-camera ReID | **FUTURE** | Architecture: `track.global_id` nullable |
| Restricted zone + night context | **MVP** | |
| Rule correlation + duplicate suppression | **MVP** | |
| Explainable risk engine (config table) | **MVP** | |
| ML risk model | **FUTURE** | |
| Incidents lifecycle + notes | **MVP** | |
| Evidence frames + SHA-256 | **MVP** | Not legal-grade |
| Evidence video clips + WORM storage | **ADVANCED** | |
| Wildlife observations from `animal` class | **MVP** | Species = `unknown` unless classifier present |
| MegaDetector / species ID | **ADVANCED** | Optional adapter |
| Movement anomaly (speed/revisit heuristic) | **MVP** | No causal claims |
| Fire/smoke from detector classes | **MVP** | No spread physics |
| Fire spread / wind-driven model | **FUTURE** | |
| Simulated ranger GPS + SOS | **MVP** | |
| Wearables / fall ML | **FUTURE** | Stub in VR-063 |
| Camera heartbeat + stall vs empty | **MVP** | |
| Tamper (scene change / covered lens heuristic) | **MVP** | Weak; labeled heuristic |
| Leaflet + OSM + PostGIS | **MVP** | |
| Command Centre | **MVP** | |
| JWT + RBAC (ADMIN, FOREST_OFFICER, RANGER, VIEWER) | **MVP** | |
| Offline outbox + sync | **MVP** | Simulated |
| Federated learning | **FUTURE** | |
| IoT sensors | **FUTURE** | Interface in VR-096 |
| Drones | **FUTURE** | Interface in VR-096 |
| Satellite | **FUTURE** | |
| Mobile ranger app | **FUTURE** | |
| Paid SMS/email | **Optional ADVANCED** | NotificationProvider no-op/log MVP |
| GPU batch inference | **ADVANCED** | CPU FPS target in MVP |

---

## 9. OPEN-SOURCE / LICENSE CHECKLIST

The application **must not** be described as “100% open source” without listing dependencies, model licenses, and dataset licenses.

Plan: VR-004 creates `docs/THIRD_PARTY_LICENSES.md` and a **license gate** in CI (manual checklist for SIH).

| Name | Repository | Purpose | License | Model license | Dataset concerns | Review? |
|------|------------|---------|---------|---------------|------------------|---------|
| Python | python.org | Runtime | PSF | n/a | n/a | No |
| FastAPI | tiangolo/fastapi | API | MIT | n/a | n/a | No |
| Pydantic v2 | pydantic/pydantic | Schemas | MIT | n/a | n/a | No |
| SQLAlchemy 2 | sqlalchemy/sqlalchemy | ORM | MIT | n/a | n/a | No |
| Alembic | sqlalchemy/alembic | Migrations | MIT | n/a | n/a | No |
| Uvicorn | encode/uvicorn | ASGI | BSD-3 | n/a | n/a | No |
| PostgreSQL | postgres | DB | PostgreSQL License | n/a | n/a | No |
| PostGIS | postgis/postgis | Spatial | **GPL-2.0** | n/a | n/a | **Yes — using as DB extension is typically OK; do not copy PostGIS source into app. Legal review for gov distribution.** |
| GeoAlchemy2 | geoalchemy/geoalchemy2 | ORM geo | MIT | n/a | n/a | No |
| OpenCV | opencv/opencv | Frames | Apache-2.0 | n/a | n/a | No |
| NumPy | numpy/numpy | Arrays | BSD-3 | n/a | n/a | No |
| ONNX Runtime | microsoft/onnxruntime | Inference | MIT | n/a | n/a | No |
| YOLOX | Megvii-BaseDetection/YOLOX | Detector | **Apache-2.0** | Weights: check release notes (often research use; confirm before gov production) | COCO (research) | **Yes for weights/COCO** |
| ByteTrack | ifzhang/ByteTrack | Tracker | **MIT** | n/a | MOT datasets | Prefer this over AGPL trackers |
| BoxMOT | mikel-brostrom/boxmot | Tracker wrappers | **AGPL-3.0** | — | — | **Do not use for MVP** unless AGPL accepted |
| Ultralytics YOLO | ultralytics/ultralytics | Detector | **AGPL-3.0** | AGPL + enterprise option | Various | **License gate: default OFF.** Optional extra if org accepts AGPL or buys license |
| MegaDetector | agentmorris/MegaDetector | Wildlife detector | Apache-2.0 (verify tag) | Model cards | Camera-trap data | ADVANCED optional |
| PyTorch | pytorch/pytorch | Only if needed | BSD-style | n/a | n/a | Avoid if ONNX-only MVP works |
| FFmpeg | FFmpeg | Decode | LGPL/GPL depending on build | n/a | n/a | **Yes — use LGPL build; no nonfree codecs in distributed images if possible** |
| Next.js | vercel/next.js | UI | MIT | n/a | n/a | No |
| React | facebook/react | UI | MIT | n/a | n/a | No |
| Tailwind CSS | tailwindlabs/tailwindcss | CSS | MIT | n/a | n/a | No |
| Leaflet | Leaflet/Leaflet | Maps | BSD-2 | n/a | n/a | No |
| React Leaflet | PaulLeCam/react-leaflet | React maps | Hippocratic-2.1 **or** check current | n/a | n/a | **Yes — Hippocratic license is not OSI; if incompatible, use Leaflet via `leaflet` + thin wrapper** |
| OpenStreetMap data | osm.org | Basemap | ODbL | n/a | Share-alike for map data extracts | **Yes if shipping extracts** |
| pytest | pytest-dev/pytest | Tests | MIT | n/a | n/a | No |
| Playwright | microsoft/playwright | E2E | Apache-2.0 | n/a | n/a | No |
| Docker | docker | Pack | Apache-2.0 | n/a | n/a | No |

**Default MVP vision stack (government-friendlier):** OpenCV + ONNX Runtime + YOLOX Apache weights (reviewed) + ByteTrack MIT + DummyDetector.  
**Ultralytics / BoxMOT:** optional extras behind `VANRAKSHA_ALLOW_AGPL=true`.

---

## 10. RISKS

| Risk | Mitigation |
|------|------------|
| Empty repo / chaotic start | Follow VR order; one TODO per PR/commit |
| YOLO false positives (humans as animals, etc.) | Confidence thresholds; DummyDetector for demos; language = verification required |
| False negatives (missed fire/person) | Multi-frame confirmation; camera health; never claim 100% detection |
| Wildlife species wrong | Default `unknown`; no “why the animal moved” |
| Night footage quality | Lower FPS, IR not assumed; night is a **risk factor**, not proof |
| AGPL infection | Default Apache/MIT stack; document Ultralytics as optional |
| PostGIS GPL confusion | Use as database; don’t vend source |
| Connectivity | Edge outbox; dashboard shows sync lag |
| Hardware lock-in | Protocols only; FileSource first |
| “Poacher” claims / legal | LANGUAGE.md + UI copy catalog + tests that forbidden strings are absent |
| Privacy (faces, rangers) | RBAC on evidence; no public internet demo without consent; retention settings |
| Security | JWT, RBAC, hashed passwords, no secrets in git, path traversal tests on evidence |
| GPU unavailable | CPU ONNX + DummyDetector; demo videos short |
| SIH demo failure | VR-093 runbook; pre-recorded pipeline replay if live inference fails |
| OSM / Leaflet license | Check react-leaflet license; OSM attribution required on map |
| Evidence overclaim | Copy: “Timestamped evidence supporting investigation, subject to applicable procedures.” |

---

## 11. DEFINITION OF DONE

### A. MVP COMPLETE

- Modular monolith runs via Docker Compose: API, worker, web, PostGIS.
- File video → detections → tracks → context → correlated event → explainable risk → incident → hashed evidence → dashboard.
- DummyDetector path works without GPU.
- At least one ONNX detector path documented (may be skipped at runtime if weights missing, with clear error).
- Four roles; login works.
- Language catalog enforced (no poacher/criminal labels).
- Simulated ranger GPS + SOS.
- Camera online/offline + empty vs stalled.
- Offline outbox sync simulated.
- Unit + integration tests for engines; one automated E2E happy path.
- THIRD_PARTY_LICENSES.md filled for actually used packages.

### B. SIH DEMO READY

MVP plus:

- Demo runbook for all 7 scenarios.
- Sample MP4s (or scripted DummyDetector timeline if video cannot ship).
- Command Centre looks like a forest operations room (map + incidents + cameras + risk).
- Live WebSocket updates visible.
- Attribution for OSM; no paid APIs required.
- Failover: if GPU/model missing, demo still runs on DummyDetector.

### C. PRODUCTION-READY ARCHITECTURE (not “production certified”)

SIH plus:

- Threat model addressed; rate limits; security headers; secret management documented.
- Backups for Postgres; evidence retention job.
- Metrics: pipeline latency, FPS, queue depth, camera freshness.
- Auth hardened; evidence access audited.
- Load notes (single-node limits).
- Legal review of model weights and PostGIS/FFmpeg distribution.
- Still **not** claimed as court-admissible evidence system or scientific fire model.

---

## 12. FINAL IMPLEMENTATION CHECKLIST

### Foundation
- [ ] Git repository initialized
- [ ] `.gitignore` / `.env.example`
- [ ] Product language spec (`docs/LANGUAGE.md`)
- [ ] Architecture ADR
- [ ] `THIRD_PARTY_LICENSES.md` skeleton + AGPL gate
- [ ] Python package + FastAPI health
- [ ] Next.js + TypeScript + Tailwind skeleton
- [ ] Docker Compose (PostGIS, API, worker, web)
- [ ] Config + structured logging

### Data
- [ ] Alembic
- [ ] Users/roles
- [ ] Forests/zones (PostGIS)
- [ ] Cameras/sources
- [ ] Detections/tracks/track_points
- [ ] Events/event_factors
- [ ] Incidents/status history
- [ ] Evidence
- [ ] Rangers/locations/patrols
- [ ] Camera health
- [ ] Notifications/audit/settings/sync_outbox
- [ ] Demo seed

### Pipeline
- [ ] VideoSource (file, webcam, RTSP stub)
- [ ] Frame sampler
- [ ] Ingestion jobs
- [ ] Detector protocol + Dummy + ONNX
- [ ] Class taxonomy + display strings
- [ ] Tracker protocol + IoU + ByteTrack
- [ ] Context provider (zone, night, proximity)
- [ ] Event engine + correlation + dedup
- [ ] Risk engine + explanations
- [ ] Incident manager + lifecycle
- [ ] Evidence store + hashes + capture

### Intelligence modules
- [ ] Wildlife observations + classifier stub + simple anomaly
- [ ] Fire/smoke events + severity heuristic (no spread)
- [ ] Ranger GPS + SOS + patrols + inactivity stub
- [ ] Camera heartbeat, stall vs empty, tamper heuristic

### Platform
- [ ] REST APIs as specified per TODO
- [ ] WebSockets
- [ ] GeoJSON + Leaflet layers
- [ ] Command Centre pages/panels
- [ ] JWT + RBAC
- [ ] Edge outbox + sync + simulator
- [ ] Dashboard statistics + outcome counters

### Quality
- [ ] Unit tests (engines, adapters)
- [ ] Integration tests (pipeline chain)
- [ ] E2E seven demos
- [ ] Security hardening + threat model
- [ ] Performance baselines + indexes + metrics
- [ ] Demo runbook + sample assets process
- [ ] Operator documentation
- [ ] Production compose + backup notes
- [ ] Sensor/drone/location stubs + model versioning layout

### Product principles (continuous)
- [ ] Software-first (no custom hardware required)
- [ ] Offline-capable architecture
- [ ] Hardware-agnostic interfaces
- [ ] No paid APIs required for MVP
- [ ] Licenses documented
- [ ] No unsupported accusations
- [ ] Explainable risk
- [ ] Evidence not claimed legal-grade

---

## How OpenCode should use this

1. Open `docs/TODOS.md`.
2. Implement **exactly one** `TODO VR-XXX`.
3. Meet ACCEPTANCE CRITERIA and TESTS.
4. Stop. Do not “continue with the next obvious feature.”
5. Review in Cursor, then proceed to the next ID in Section 7.

---

*End of master plan overview. Atomic tasks follow in `docs/TODOS.md`.*
