# VANRAKSHA AI — ATOMIC TODOS (VR-001 … VR-096)

Execute **one** TODO per agent session. Paths are from repository root `VANRAKSHA-AI/`.  
Greenfield: files listed under FILES TO CREATE do not exist until that TODO.

Shared contracts referenced throughout are defined at first use and must not be silently changed later.

---

## PHASE 0 — Repository Audit & Architecture

### TODO VR-001 — Initialize Git repository and ignore rules

OBJECTIVE:
Create version control and ignore Python, Node, models, env files, OS junk, and large videos.

FILES TO CREATE:
- `.gitignore` — ignore rules
- `.gitattributes` — LF for source; `*.mp4 binary`

FILES TO MODIFY:
- none

IMPLEMENTATION:
Run `git init` in the workspace root. Add `.gitignore` covering: `__pycache__/`, `.venv/`, `node_modules/`, `.next/`, `.env`, `.env.local`, `models/*.onnx`, `models/*.pt`, `samples/videos/*.mp4`, `backend/.pytest_cache/`, `coverage/`, `.DS_Store`, `Thumbs.db`, editor folders. Keep `docs/`, `*.md`, `samples/videos/.gitkeep` tracked.

INTERFACES / CONTRACTS:
None.

DEPENDENCIES:
None (empty repo).

INPUTS:
Empty workspace.

OUTPUTS:
Git repo with initial commit allowed after this TODO (implementation agent may commit only if the human asked; otherwise just files).

ACCEPTANCE CRITERIA:
- `git status` works.
- `.env` and `*.onnx` would be ignored (verify with `git check-ignore -v`).

TESTS:
- Shell: `git check-ignore -v .env models/foo.onnx samples/videos/demo.mp4` returns ignore matches.

DO NOT:
- Do not add application source yet.
- Do not force-push or configure git user.
- Do not commit secrets.

---

### TODO VR-002 — Product language and terminology specification

OBJECTIVE:
Lock wording so the system never presents inference as fact (no “poacher detected”).

FILES TO CREATE:
- `docs/LANGUAGE.md` — terminology
- `backend/app/core/language.py` — string catalog + forbidden-term checker (can be a stub module until backend package exists; if `backend/` not created yet, create only `docs/LANGUAGE.md` AND `shared/language_catalog.yaml` then VR-005 moves it — **prefer** `docs/LANGUAGE.md` + `config/language_catalog.yaml` now)

FILES TO MODIFY:
- none

IMPLEMENTATION:
Document the four layers: Detection, Inference, Risk assessment, Human verification.  
Define event `language_key` values: `person_detected`, `vehicle_detected`, `animal_detected`, `smoke_detected`, `fire_detected`, `suspicious_activity`, `suspicious_activity_high_risk`, `wildlife_unusual_movement`, `camera_tampering_suspected`, `camera_failure_suspected`, `ranger_sos`, `restricted_zone_activity`.  
User-facing templates must include verification language for HIGH/CRITICAL.  
Forbidden substrings for automated copy: `poacher`, `poaching`, `criminal`, `guilty`, `smuggler`, `terrorist` (unless inside a comment explaining they are forbidden).  
Evidence disclaimer: “Timestamped evidence supporting investigation, subject to applicable procedures.”

INTERFACES / CONTRACTS:
`config/language_catalog.yaml`:
```yaml
forbidden_terms: [poacher, poaching, ...]
messages:
  suspicious_activity_high_risk:
    title: "High-risk suspicious activity detected"
    body: "Ranger verification required."
    layer: risk
```
Python helper (if package exists) `assert_copy_allowed(text: str) -> None`.

DEPENDENCIES:
VR-001

INPUTS:
Product principles from roadmap.

OUTPUTS:
Catalog consumed by EventEngine, RiskEngine, frontend copy.

ACCEPTANCE CRITERIA:
- Catalog contains all keys listed above.
- Forbidden terms documented.
- Disclaimers for evidence and wildlife (“Unusual movement detected; ranger verification recommended.”).

TESTS:
- `tests/unit/test_language_catalog.py` (create tests dir if needed): load YAML; every message body for risk-level keys contains “verification”; forbidden terms do not appear in `messages.*.title/body`.

DO NOT:
- Do not implement engines.
- Do not add more accusatory event types.

---

### TODO VR-003 — Architecture decision record (stack lock)

OBJECTIVE:
Record the modular-monolith stack so later TODOs do not invent microservices.

FILES TO CREATE:
- `docs/ARCHITECTURE.md`

FILES TO MODIFY:
- none

IMPLEMENTATION:
Write ADR covering: modular monolith; FastAPI; Next.js App Router + TS; PostgreSQL 16 + PostGIS 3; ONNX Runtime + YOLOX default detector; ByteTrack MIT; DummyDetector; Leaflet (check react-leaflet license in VR-004); WebSockets; Docker Compose; pytest + Playwright. Explicitly reject for MVP: Kafka, Redis, K8s, Ultralytics unless AGPL flag, BoxMOT, paid APIs. Diagram the pipeline from Section 2 of `docs/IMPLEMENTATION_ROADMAP.md`. List all Protocol names: VideoSource, Detector, Tracker, ContextProvider, EventEngine, RiskEngine, IncidentManager, EvidenceStore, NotificationProvider, LocationProvider, SensorSource, DroneSource, CameraHealthMonitor.

INTERFACES / CONTRACTS:
Document only; no code.

DEPENDENCIES:
VR-002

INPUTS:
Roadmap Section 2.

OUTPUTS:
Binding ADR for implementers.

ACCEPTANCE CRITERIA:
- ADR states “modular monolith”.
- License-sensitive choices called out (PostGIS GPL, Ultralytics AGPL, FFmpeg).

TESTS:
- None automated. Human: file exists and mentions each Protocol name.

DO NOT:
- Do not generate code scaffolding here beyond the markdown file.

---

### TODO VR-004 — Third-party license registry and AGPL gate

OBJECTIVE:
Create living license documentation and a default-deny AGPL policy.

FILES TO CREATE:
- `docs/THIRD_PARTY_LICENSES.md`
- `config/license_policy.yaml`

FILES TO MODIFY:
- `docs/ARCHITECTURE.md` — link to this file

IMPLEMENTATION:
Copy the dependency table from roadmap Section 9 as the starting inventory. Mark each as `planned` until added to `pyproject.toml`/`package.json`. Set `allow_agpl: false`. Document that React Leaflet’s license must be re-verified; if Hippocratic, use vanilla Leaflet.

INTERFACES / CONTRACTS:
`license_policy.yaml`: `allow_agpl: false`, `forbidden_packages: [ultralytics, boxmot]` unless allow_agpl.

DEPENDENCIES:
VR-003

INPUTS:
Section 9 table.

OUTPUTS:
Policy file later checked in CI (VR-091).

ACCEPTANCE CRITERIA:
- File states the project is **not** “100% open source” as a blanket claim.
- YOLOX vs Ultralytics decision recorded.

TESTS:
- Unit test later in VR-005+ that `license_policy.yaml` parses. For this TODO: YAML valid.

DO NOT:
- Do not add Ultralytics to the default dependency list.
- Do not give legal advice as certainty; mark “requires additional review”.

---

## PHASE 1 — Project Foundation

### TODO VR-005 — Python backend package skeleton

OBJECTIVE:
Create an installable Python package `vanraksha` / `app` with tooling.

FILES TO CREATE:
- `pyproject.toml` — project metadata, deps: fastapi, uvicorn, pydantic-settings, sqlalchemy, alembic, psycopg, geoalchemy2, numpy, opencv-python-headless, onnxruntime, pyyaml, httpx, pytest, pytest-asyncio
- `backend/app/__init__.py`
- `backend/app/main.py` — placeholder `FastAPI(title="VANRAKSHA AI")` with no routers yet except imported later
- `backend/tests/conftest.py`
- `backend/tests/unit/test_health_placeholder.py` — skip or import app
- `README.md` — project name, tagline, how to run (minimal)

FILES TO MODIFY:
- `.gitignore` if needed

IMPLEMENTATION:
Package dir `backend/app`. `pyproject.toml` at root with `tool.pytest.ini_options` `pythonpath = ["backend"]`. Pin major versions reasonably. Do not add ultralytics.

INTERFACES / CONTRACTS:
Package import: `from app.main import app`.

DEPENDENCIES:
VR-001, VR-004 (policy)

INPUTS:
ADR.

OUTPUTS:
`pip install -e .` works.

ACCEPTANCE CRITERIA:
- `python -c "from app.main import app"` from configured path works.
- No AGPL packages in default deps.

TESTS:
- `pytest backend/tests/unit/test_health_placeholder.py` collects.

DO NOT:
- Do not connect to a database yet.
- Do not add frontend.

---

### TODO VR-006 — FastAPI health and readiness endpoints

OBJECTIVE:
Expose liveness and readiness for Compose healthchecks.

FILES TO CREATE:
- `backend/app/api/v1/health.py`
- `backend/app/api/router.py`
- `backend/tests/unit/test_health.py`

FILES TO MODIFY:
- `backend/app/main.py` — include router prefix `/api/v1`

IMPLEMENTATION:
`GET /api/v1/health/live` → `{status: "ok"}` always.  
`GET /api/v1/health/ready` → `{status: "ok"|"degraded", db: bool}` — db false until VR-012, return 200 with `db: false` OR 503; pick **200 + db:false** until DB exists so Compose does not flap, then VR-012 switches ready to require DB.

INTERFACES / CONTRACTS:
```json
{"status": "ok", "db": false, "version": "0.1.0"}
```

DEPENDENCIES:
VR-005

INPUTS:
FastAPI app.

OUTPUTS:
Health API.

ACCEPTANCE CRITERIA:
- Live always 200.
- OpenAPI shows both routes.

TESTS:
- httpx `TestClient`: live 200; ready JSON has `db` key.

DO NOT:
- Do not add auth to health live (ready may stay public).

---

### TODO VR-007 — Settings from environment

OBJECTIVE:
Centralize configuration; no secrets in code.

FILES TO CREATE:
- `.env.example`
- `backend/app/core/config.py`

FILES TO MODIFY:
- `backend/app/main.py` — use settings for title/debug

IMPLEMENTATION:
`pydantic_settings.BaseSettings` with: `database_url`, `secret_key`, `cors_origins`, `edge_mode: bool`, `allow_agpl: bool = False`, `models_dir`, `evidence_dir`, `sample_fps: float = 2.0`, `jwt_expire_minutes`, `demo_mode: bool`. Load `.env`. Fail fast if `secret_key` is default in `ENV=production` (production check can warn in MVP).

INTERFACES / CONTRACTS:
`get_settings() -> Settings` lru_cached. Tests override via env.

DEPENDENCIES:
VR-006

INPUTS:
`.env.example` keys.

OUTPUTS:
Typed settings.

ACCEPTANCE CRITERIA:
- `.env.example` has every key with dummy values.
- `SECRET_KEY` not hardcoded in source.

TESTS:
- `test_config.py`: monkeypatch env; settings parse.

DO NOT:
- Do not commit `.env`.

---

### TODO VR-008 — Structured logging

OBJECTIVE:
JSON-capable structured logs with request id.

FILES TO CREATE:
- `backend/app/core/logging.py`
- `backend/app/core/middleware.py`

FILES TO MODIFY:
- `backend/app/main.py` — configure logging, add middleware

IMPLEMENTATION:
Use stdlib logging. Format: timestamp, level, logger, message, request_id, camera_id optional. Middleware assigns `X-Request-ID`. Never log raw image bytes or JWT.

INTERFACES / CONTRACTS:
`get_logger(name: str) -> logging.Logger`

DEPENDENCIES:
VR-007

INPUTS:
Settings.debug for pretty vs JSON.

OUTPUTS:
Request-scoped logs.

ACCEPTANCE CRITERIA:
- One request produces a log line containing request id.

TESTS:
- TestClient call; caplog has request id.

DO NOT:
- Do not add Datadog/Sentry paid SaaS.

---

### TODO VR-009 — Next.js Command Centre skeleton

OBJECTIVE:
Create TypeScript Next.js app with Tailwind and forest-operations visual baseline (dark, high contrast, not generic SaaS purple).

FILES TO CREATE:
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/next.config.ts`
- `frontend/tailwind.config.ts`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx` — placeholder “VANRAKSHA AI — Forest Command Centre”
- `frontend/src/app/globals.css`

FILES TO MODIFY:
- `README.md` — frontend dev instructions

IMPLEMENTATION:
Next.js App Router, React 19 or current LTS, Tailwind. Root page is a full-viewport shell with header “VANRAKSHA AI” and tagline. No auth yet. Use OSM-safe fonts (system stack).

INTERFACES / CONTRACTS:
App runs on port 3000; `NEXT_PUBLIC_API_URL` default `http://localhost:8000`.

DEPENDENCIES:
VR-001

INPUTS:
ADR frontend choice.

OUTPUTS:
`npm run dev` works.

ACCEPTANCE CRITERIA:
- Typecheck passes.
- Home page renders product name.

TESTS:
- `npm run build` succeeds (or `npx tsc --noEmit`).

DO NOT:
- Do not install paid UI kits.
- Do not implement map/incidents yet.
- Do not add react-leaflet until VR-004 license re-check in this TODO’s IMPLEMENTATION notes: prefer `leaflet` + useEffect wrapper if Hippocratic.

---

### TODO VR-010 — Docker Compose for local stack

OBJECTIVE:
One-command local infrastructure: PostGIS, API, web, worker stub.

FILES TO CREATE:
- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/app/worker.py` — process that logs “worker idle” until pipeline exists

FILES TO MODIFY:
- `.env.example` — compose variables
- `README.md`

IMPLEMENTATION:
Service `db`: `postgis/postgis:16-3.4` (or current 16-3.x), volume, port 5432, POSTGRES_DB=vanraksha.  
Service `api`: build backend, command uvicorn, depends_on db, port 8000.  
Service `web`: frontend, port 3000.  
Service `worker`: same image as api, `python -m app.worker`.  
Healthcheck db `pg_isready`. Network internal.

INTERFACES / CONTRACTS:
Compose project name `vanraksha`.

DEPENDENCIES:
VR-007, VR-009

INPUTS:
Dockerfiles.

OUTPUTS:
`docker compose up --build` starts (worker may idle).

ACCEPTANCE CRITERIA:
- compose file validates (`docker compose config`).
- db image is PostGIS not vanilla Postgres.

TESTS:
- CI-less: `docker compose config` exit 0.

DO NOT:
- Do not add Redis/Kafka.
- Do not write Kubernetes manifests.

---

### TODO VR-011 — Developer scripts

OBJECTIVE:
Windows-friendly and Unix-friendly commands for install, migrate, test, demo.

FILES TO CREATE:
- `Makefile` — `dev`, `test`, `migrate`, `lint` targets calling compose/pytest
- `scripts/dev.ps1` — PowerShell equivalents
- `scripts/download_models.py` — stub printing where to place ONNX (no download of unlicensed weights yet)

FILES TO MODIFY:
- `README.md`

IMPLEMENTATION:
Document Python 3.11+. Scripts must not require paid tools.

INTERFACES / CONTRACTS:
`make test` → pytest backend.

DEPENDENCIES:
VR-010

INPUTS:
Existing layout.

OUTPUTS:
Documented commands.

ACCEPTANCE CRITERIA:
- README lists exact commands for Windows PowerShell.

TESTS:
- `pwsh -File scripts/dev.ps1 -Help` or script comments; Makefile has `test` target.

DO NOT:
- Do not download large weights in this TODO.

---

## PHASE 2 — Infrastructure & Database

### TODO VR-012 — SQLAlchemy engine, session, GeoAlchemy base

OBJECTIVE:
Wire database connectivity and session dependency.

FILES TO CREATE:
- `backend/app/db/base.py` — DeclarativeBase
- `backend/app/db/session.py` — engine, SessionLocal, `get_db`
- `backend/tests/unit/test_db_session.py`

FILES TO MODIFY:
- `backend/app/api/v1/health.py` — ready checks `SELECT 1` when URL set
- `backend/app/core/config.py` if needed

IMPLEMENTATION:
SQLAlchemy 2.x. Use `postgresql+psycopg://`. Enable PostGIS in a later migration; engine create_all **forbidden** in production — Alembic only (VR-013). Tests may use SQLite **only for non-geo unit tests**; geo tests require Postgres (mark `pytest.mark.geo`).

INTERFACES / CONTRACTS:
`get_db()` generator yields `Session`.

DEPENDENCIES:
VR-007, VR-010

INPUTS:
`DATABASE_URL`.

OUTPUTS:
Working sessions.

ACCEPTANCE CRITERIA:
- Ready endpoint reports `db: true` when Postgres up.

TESTS:
- Unit test get_db with sqlite in-memory for smoke; optional skip if no driver.

DO NOT:
- Do not create domain tables yet.
- Do not use GeoAlchemy columns until VR-015.

---

### TODO VR-013 — Alembic setup

OBJECTIVE:
Migration framework from empty DB to all future schemas.

FILES TO CREATE:
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/.gitkeep`

FILES TO MODIFY:
- `pyproject.toml` if script entry `vanraksha-migrate`

IMPLEMENTATION:
`env.py` imports `app.db.base.Base` and all models as they appear. Autogenerate allowed but review required. First empty revision optional.

INTERFACES / CONTRACTS:
`alembic -c backend/alembic.ini upgrade head`

DEPENDENCIES:
VR-012

INPUTS:
Engine URL from settings.

OUTPUTS:
Migration toolchain.

ACCEPTANCE CRITERIA:
- `upgrade head` succeeds on empty PostGIS container.

TESTS:
- Document command; optional test that env.py imports.

DO NOT:
- Do not squash later TODOs into one giant migration in this task — later TODOs add revisions.

---

### TODO VR-014 — Users, roles, and auth tables

OBJECTIVE:
Minimum identity schema for RBAC.

FILES TO CREATE:
- `backend/app/models/user.py`
- `backend/app/models/enums.py` — `UserRole = ADMIN | FOREST_OFFICER | RANGER | VIEWER`
- `backend/alembic/versions/xxxx_users.py`
- `backend/tests/unit/test_models_user.py`

FILES TO MODIFY:
- `backend/app/db/base.py` — import models

IMPLEMENTATION:
Tables: `users` (id UUID PK, email unique, hashed_password, full_name, role, ranger_id nullable FK later, is_active, created_at, updated_at). Do not implement JWT yet (VR-083). Password column exists. Enum in DB as string.

INTERFACES / CONTRACTS:
SQLAlchemy `User`. Pydantic schemas in VR-020+.

DEPENDENCIES:
VR-013

INPUTS:
Role list from product.

OUTPUTS:
`users` table.

ACCEPTANCE CRITERIA:
- Migration applies; role constraint or check in app.

TESTS:
- Model create in session (sqlite or postgres).

DO NOT:
- Do not add OAuth/social login.
- Do not add extra roles unless documented in LANGUAGE/ARCHITECTURE.

---

### TODO VR-015 — Forests, zones, cameras (PostGIS)

OBJECTIVE:
Geospatial operational picture: forest areas, named zones including restricted, cameras with point location.

FILES TO CREATE:
- `backend/app/models/forest.py` — ForestArea
- `backend/app/models/zone.py` — Zone (`zone_type`: patrol, restricted, corridor, buffer, other)
- `backend/app/models/camera.py` — Camera, CameraSource
- `backend/alembic/versions/xxxx_geo_cameras.py` — `CREATE EXTENSION IF NOT EXISTS postgis;`
- `backend/tests/geo/test_zone_contains.py`

FILES TO MODIFY:
- none besides alembic env imports

IMPLEMENTATION:
`forest_areas`: id, name, geom Polygon 4326.  
`zones`: id, forest_id, name, zone_type, is_restricted bool, geom Polygon 4326.  
`cameras`: id, name, code unique, forest_id, location Point 4326, heading_deg nullable, status enum planned/active/offline, is_simulated bool.  
`camera_sources`: id, camera_id, source_type enum file|webcam|rtsp|other, uri (file path or rtsp url), extra_json.  
GIST indexes on all geoms.

INTERFACES / CONTRACTS:
SRID 4326 everywhere.

DEPENDENCIES:
VR-014

INPUTS:
PostGIS.

OUTPUTS:
Geo tables.

ACCEPTANCE CRITERIA:
- Extension postgis enabled.
- Can insert a polygon and point.

TESTS:
- `test_zone_contains`: camera point in restricted polygon → ST_Contains true.

DO NOT:
- Do not implement GeoJSON API yet (VR-069).
- Do not add 3D/raster.

---

### TODO VR-016 — Detections, tracks, track_points

OBJECTIVE:
Persist vision outputs without events yet.

FILES TO CREATE:
- `backend/app/models/detection.py`
- `backend/app/models/track.py`
- `backend/alembic/versions/xxxx_vision.py`
- `backend/tests/unit/test_models_vision.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
`detections`: id, camera_id, frame_seq, captured_at timestamptz, class_name, class_id int, confidence float, bbox_xyxy jsonb, centroid geometry(Point,4326) nullable (image-space stored as bbox; map-space optional if camera homography absent — **MVP: store image bbox + optional map_point if camera has location only as camera point not object GPS**), track_id nullable FK, detector_id, model_version, extra_json.  
`tracks`: id UUID, camera_id, local_track_id int, class_name, first_seen, last_seen, confidence_avg, status active|ended, global_id nullable (FUTURE ReID).  
`track_points`: id, track_id, captured_at, bbox_xyxy, centroid_image jsonb `{x,y}`, map_point geography nullable.

INTERFACES / CONTRACTS:
Detection is frame-level; Track is temporal. Do not put risk scores on detections.

DEPENDENCIES:
VR-015

INPUTS:
Camera FK.

OUTPUTS:
Vision tables.

ACCEPTANCE CRITERIA:
- Indexes: (camera_id, captured_at), (track_id, captured_at).

TESTS:
- Insert detection + track + point.

DO NOT:
- Do not add species columns on detections (wildlife table later).
- Do not implement ReID.

---

### TODO VR-017 — Events, event_factors, incidents, evidence metadata

OBJECTIVE:
Operational case tables plus factor breakdown storage.

FILES TO CREATE:
- `backend/app/models/event.py`
- `backend/app/models/incident.py`
- `backend/app/models/evidence.py`
- `backend/alembic/versions/xxxx_ops.py`
- `backend/tests/unit/test_models_ops.py`

FILES TO MODIFY:
- `backend/app/models/enums.py` — IncidentStatus, EventType, RiskLevel

IMPLEMENTATION:
`events`: id, camera_id, event_type, language_key, correlation_key, window_start, window_end, location geometry(Point,4326), risk_score nullable, risk_level nullable, payload jsonb, created_at.  
`event_factors`: id, event_id, code, delta int, reason text.  
`event_tracks` M2M event_id, track_id.  
`incidents`: id, public_id str unique (e.g. INC-2026-0001), title, language_key, status, risk_score, risk_level, location, assigned_user_id nullable, resolution_notes, created_at, updated_at.  
`incident_events` M2M.  
`incident_status_history`: id, incident_id, from_status, to_status, actor_user_id, note, at.  
`evidence`: id, incident_id nullable, event_id nullable, camera_id, kind frame|clip|json, storage_uri, sha256, captured_at, bbox_xyxy jsonb, disclaimer_key, extra_json.

INTERFACES / CONTRACTS:
IncidentStatus: `NEW | ACKNOWLEDGED | INVESTIGATING | DISPATCHED | RESOLVED | CLOSED`.  
RiskLevel: `LOW | MEDIUM | HIGH | CRITICAL`.

DEPENDENCIES:
VR-016, VR-002

INPUTS:
Language keys.

OUTPUTS:
Ops tables.

ACCEPTANCE CRITERIA:
- Status enum matches list.
- Evidence has sha256 column.

TESTS:
- Create incident with history row.

DO NOT:
- Do not auto-set status CLOSED from AI.
- Do not claim legal chain-of-custody beyond hash field.

---

### TODO VR-018 — Rangers, locations, patrols, camera_health, notifications, audit, settings, sync_outbox

OBJECTIVE:
Remaining MVP tables in one migration (still one concern: supporting systems).

FILES TO CREATE:
- `backend/app/models/ranger.py`
- `backend/app/models/camera_health.py`
- `backend/app/models/notification.py`
- `backend/app/models/audit.py`
- `backend/app/models/settings.py`
- `backend/app/models/sync.py`
- `backend/alembic/versions/xxxx_support.py`
- `backend/tests/unit/test_models_support.py`

FILES TO MODIFY:
- `users.ranger_id` FK if not done

IMPLEMENTATION:
`rangers`: id, badge_code unique, name, is_simulated, active.  
`ranger_locations`: id, ranger_id, captured_at, geom Point 4326, source simulated|gps|manual, accuracy_m.  
`patrols`: id, ranger_id, started_at, ended_at nullable, status, route_geom LineString nullable.  
`camera_health`: id, camera_id unique, state online|offline|degraded|unknown, last_heartbeat, last_frame_at, last_detection_at, notes, extra_json.  
`notifications`: id, incident_id nullable, channel in_app|ws, title, body, language_key, read_at.  
`audit_logs`: id, actor_user_id, action, entity_type, entity_id, at, payload jsonb.  
`system_settings`: key PK, value jsonb (risk weights live here).  
`sync_outbox`: id, idempotency_key unique, payload jsonb, created_at, synced_at nullable, attempts int.

INTERFACES / CONTRACTS:
Health state enum as above.  
Default risk weights JSON written in VR-046 seed.

DEPENDENCIES:
VR-017, VR-014

INPUTS:
Schema plan.

OUTPUTS:
Support tables.

ACCEPTANCE CRITERIA:
- `sync_outbox.idempotency_key` unique.
- `system_settings` can store `{factors: [...]}`.

TESTS:
- Insert ranger location with Point.

DO NOT:
- Do not implement wearable BLE.
- Do not add Kafka outbox connectors.

---

### TODO VR-019 — Demo forest seed

OBJECTIVE:
Deterministic demo geography and cameras for all later scenarios.

FILES TO CREATE:
- `samples/geo/demo_forest.geojson`
- `scripts/seed_demo.py`
- `backend/app/services/seed.py`

FILES TO MODIFY:
- `README.md` — seed command

IMPLEMENTATION:
Create fictional “Vanraksha Demo Reserve” polygon, one restricted zone, one corridor zone, three cameras (file sources pointing to `samples/videos/...` placeholders), two simulated rangers, default admin user with hashed password `changeme` only if `DEMO_MODE=true`. Night window in settings 18:00–06:00 local Asia/Kolkata.

INTERFACES / CONTRACTS:
Seed is idempotent (upsert by camera.code, ranger.badge_code).

DEPENDENCIES:
VR-018, VR-007

INPUTS:
GeoJSON.

OUTPUTS:
DB rows for demos.

ACCEPTANCE CRITERIA:
- Running seed twice does not duplicate cameras.
- At least one restricted zone.

TESTS:
- `test_seed_idempotent.py` using test DB.

DO NOT:
- Do not use real ranger PII.
- Do not claim the polygon is a real sanctuary boundary.

---

## PHASE 3 — Backend Core

### TODO VR-020 — Shared API schemas, errors, pagination

OBJECTIVE:
Uniform request/response and error envelopes.

FILES TO CREATE:
- `backend/app/schemas/common.py` — Paginated[T], ErrorBody
- `backend/app/core/errors.py` — AppError, codes
- `backend/app/api/deps.py` — pagination query params
- `backend/tests/unit/test_error_handler.py`

FILES TO MODIFY:
- `backend/app/main.py` — exception handlers

IMPLEMENTATION:
Errors: `{code, message, details, request_id}`. HTTP 422 from Pydantic stays. Pagination: `limit` 1–100 default 20, `offset`. Never leak stack traces in production.

INTERFACES / CONTRACTS:
`ErrorBody`. `Page{ items, total, limit, offset }`.

DEPENDENCIES:
VR-008

INPUTS:
FastAPI.

OUTPUTS:
Consistent API errors.

ACCEPTANCE CRITERIA:
- Unknown route 404 uses envelope.
- Raised AppError maps to status.

TESTS:
- TestClient 404 JSON shape; AppError 400.

DO NOT:
- Do not return ORM objects from routes.

---

### TODO VR-021 — Camera management API

OBJECTIVE:
CRUD cameras and sources (file/webcam/rtsp metadata).

FILES TO CREATE:
- `backend/app/schemas/camera.py`
- `backend/app/services/camera_service.py`
- `backend/app/api/v1/cameras.py`
- `backend/tests/integration/test_cameras_api.py`

FILES TO MODIFY:
- `backend/app/api/router.py`

IMPLEMENTATION:
`GET/POST /api/v1/cameras`  
`GET/PATCH/DELETE /api/v1/cameras/{id}`  
`POST /api/v1/cameras/{id}/sources`  
Validate source_type; do not open video here. Geo: accept GeoJSON Point. Auth later; for now leave routes open but mark `TODO auth VR-083` in router comments. DELETE is soft: `status=retired` if you add that enum value, else `is_active=false` — add `is_active` if missing.

INTERFACES / CONTRACTS:
`CameraCreate`, `CameraRead` (include location lon/lat).

DEPENDENCIES:
VR-015, VR-020

INPUTS:
Seed optional.

OUTPUTS:
Camera API.

ACCEPTANCE CRITERIA:
- Create camera with point; list returns it.
- Invalid GeoJSON 422.

TESTS:
- Integration tests with test Postgres or sqlite skip geo — prefer docker db.

DO NOT:
- Do not start FFmpeg.
- Do not implement RTSP connect.

---

### TODO VR-022 — Zone and forest APIs

OBJECTIVE:
CRUD forest areas and zones including `is_restricted`.

FILES TO CREATE:
- `backend/app/schemas/zone.py`
- `backend/app/services/zone_service.py`
- `backend/app/api/v1/zones.py`
- `backend/app/api/v1/forests.py`
- `backend/tests/integration/test_zones_api.py`

FILES TO MODIFY:
- router

IMPLEMENTATION:
CRUD `/api/v1/forests`, `/api/v1/zones`. Polygon GeoJSON. Query `?restricted=true`.

INTERFACES / CONTRACTS:
`ZoneRead` includes `is_restricted`, `zone_type`.

DEPENDENCIES:
VR-021

INPUTS:
PostGIS.

OUTPUTS:
Zone API.

ACCEPTANCE CRITERIA:
- Restricted filter works.

TESTS:
- Create zone polygon; GET filter.

DO NOT:
- Do not compute risk here.

---

### TODO VR-023 — Ranger profile API (no GPS stream yet)

OBJECTIVE:
CRUD rangers for assignment and map later.

FILES TO CREATE:
- `backend/app/schemas/ranger.py`
- `backend/app/services/ranger_service.py`
- `backend/app/api/v1/rangers.py`
- `backend/tests/integration/test_rangers_api.py`

FILES TO MODIFY:
- router

IMPLEMENTATION:
CRUD `/api/v1/rangers`. No SOS yet.

INTERFACES / CONTRACTS:
`RangerRead`.

DEPENDENCIES:
VR-018, VR-020

INPUTS:
rangers table.

OUTPUTS:
Ranger API.

ACCEPTANCE CRITERIA:
- Unique badge_code 409/422.

TESTS:
- Create/list/get.

DO NOT:
- Do not implement mobile app.
- Do not fake fall detection.

---

### TODO VR-024 — System settings API (admin)

OBJECTIVE:
Read/update JSON settings including future risk weights placeholder empty.

FILES TO CREATE:
- `backend/app/schemas/settings.py`
- `backend/app/services/settings_service.py`
- `backend/app/api/v1/settings.py`
- `backend/tests/integration/test_settings_api.py`

FILES TO MODIFY:
- router

IMPLEMENTATION:
`GET /api/v1/settings/{key}` `PUT /api/v1/settings/{key}`. Seed key `risk_weights` as `{}` until VR-046. Comment that VR-083 must restrict to ADMIN.

INTERFACES / CONTRACTS:
Value is arbitrary JSON object.

DEPENDENCIES:
VR-018, VR-020

INPUTS:
system_settings.

OUTPUTS:
Settings API.

ACCEPTANCE CRITERIA:
- PUT then GET roundtrip.

TESTS:
- Roundtrip test.

DO NOT:
- Do not hardcode risk weights in Python constants as the only source of truth (defaults OK in code, DB overrides).

---

## PHASE 4 — Video Ingestion

### TODO VR-025 — VideoSource protocol and Frame contract

OBJECTIVE:
Hardware-agnostic video interface.

FILES TO CREATE:
- `backend/app/sources/__init__.py`
- `backend/app/sources/base.py`
- `backend/app/sources/types.py`
- `backend/tests/unit/test_video_source_protocol.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
```python
@dataclass
class Frame:
    camera_id: UUID
    source_id: UUID | None
    captured_at: datetime  # UTC
    seq: int
    image_bgr: np.ndarray  # HxWx3 uint8
    width: int
    height: int

class VideoSource(Protocol):
    def open(self) -> None: ...
    def read_frame(self) -> Frame | None: ...  # None = EOF or disconnect
    def close(self) -> None: ...
    def metadata(self) -> VideoSourceMetadata: ...
```
`VideoSourceMetadata`: fps_nominal, uri_redacted, source_type.

INTERFACES / CONTRACTS:
`Frame`, `VideoSource` as above. Downstream must depend only on these.

DEPENDENCIES:
VR-005

INPUTS:
None.

OUTPUTS:
Contracts for VR-026–028.

ACCEPTANCE CRITERIA:
- Protocol documented in docstrings.
- typing check: FileSource will implement in next TODOs.

TESTS:
- A dummy `ListVideoSource` in tests yields two frames then None.

DO NOT:
- Do not import vendor SDKs.
- Do not call detectors.

---

### TODO VR-026 — FileVideoSource (MP4 simulation)

OBJECTIVE:
Primary MVP camera simulation from disk.

FILES TO CREATE:
- `backend/app/sources/file_source.py`
- `backend/tests/unit/test_file_source.py`
- `samples/videos/.gitkeep`
- `samples/README.md` — how to add MP4s

FILES TO MODIFY:
- none

IMPLEMENTATION:
OpenCV `VideoCapture(path)`. Map frame timestamps as `start_time + seq/fps`. Handle missing file with AppError. `read_frame` returns None at EOF. Optional loop flag `loop: bool=False`.

INTERFACES / CONTRACTS:
`FileVideoSource(camera_id, path: Path, *, loop=False) -> VideoSource`

DEPENDENCIES:
VR-025, VR-021 (camera_id)

INPUTS:
MP4 path. Tests use a tiny generated video via OpenCV VideoWriter in tmp (no binary commit).

OUTPUTS:
Frames from files.

ACCEPTANCE CRITERIA:
- Reads all frames of synthetic 5-frame video.
- Missing file raises clear error.

TESTS:
- Generate temp mp4; count frames; close releases capture.

DO NOT:
- Do not require RTSP.
- Do not commit large videos.

---

### TODO VR-027 — WebcamVideoSource

OBJECTIVE:
Optional local webcam without breaking headless servers.

FILES TO CREATE:
- `backend/app/sources/webcam_source.py`
- `backend/tests/unit/test_webcam_source.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
`WebcamVideoSource(camera_id, device_index: int = 0)`. If open fails, raise `WebcamUnavailable`. Tests skip if no device (`pytest.mark.skipif`).

INTERFACES / CONTRACTS:
Implements `VideoSource`.

DEPENDENCIES:
VR-025

INPUTS:
Device index.

OUTPUTS:
Live frames when hardware present.

ACCEPTANCE CRITERIA:
- Instantiating with impossible index fails cleanly.
- Does not crash import on servers without V4L.

TESTS:
- Fail-closed on bad index; skip live read.

DO NOT:
- Do not make webcam required for MVP.

---

### TODO VR-028 — RTSPVideoSource abstraction

OBJECTIVE:
RTSP-ready adapter; live optional.

FILES TO CREATE:
- `backend/app/sources/rtsp_source.py`
- `backend/tests/unit/test_rtsp_source.py`

FILES TO MODIFY:
- `backend/app/sources/factory.py` — `build_source(camera_source_row) -> VideoSource`

IMPLEMENTATION:
OpenCV VideoCapture(rtsp_url). Timeout/reconnect: MVP `open()` retries 3 times then None reads. Factory maps source_type to File/Webcam/RTSP. Do not log passwords in URI (redact in metadata).

INTERFACES / CONTRACTS:
`build_source(...)` used by ingestion job.

DEPENDENCIES:
VR-026, VR-027, VR-021

INPUTS:
camera_sources.uri

OUTPUTS:
Factory.

ACCEPTANCE CRITERIA:
- Factory returns FileVideoSource for file type.
- RTSP metadata redacts credentials.

TESTS:
- Factory unit tests with fake paths; RTSP not required live.

DO NOT:
- Do not require a physical IP camera for tests.
- Do not bind to a vendor ONVIF SDK.

---

### TODO VR-029 — FrameSampler and ingestion jobs

OBJECTIVE:
Control pipeline rate and run ingest as a job.

FILES TO CREATE:
- `backend/app/pipeline/sampler.py`
- `backend/app/models/ingest_job.py` + alembic revision
- `backend/app/services/ingest_service.py`
- `backend/app/api/v1/ingest.py`
- `backend/app/pipeline/runner.py` — loop: source → sample → callback (no detect yet; callback records last_frame_at)
- `backend/tests/unit/test_sampler.py`
- `backend/tests/integration/test_ingest_api.py`

FILES TO MODIFY:
- `backend/app/worker.py` — poll jobs `queued` and run
- camera_health last_frame_at update

IMPLEMENTATION:
`FrameSampler(target_fps: float)`: keep frame if elapsed >= 1/target_fps.  
Jobs: `POST /api/v1/ingest/jobs {camera_id}` starts; `POST .../stop`; `GET .../{id}`. Status queued|running|completed|failed|stopped. Worker thread/async: **use a background asyncio task in worker process**, not Celery.

INTERFACES / CONTRACTS:
`PipelineStep` callback `async def on_frame(frame: Frame) -> None` registered later.

DEPENDENCIES:
VR-028, VR-018

INPUTS:
Frames, settings.sample_fps.

OUTPUTS:
Ingestion control API + sampler.

ACCEPTANCE CRITERIA:
- Sampler at 2 FPS on 10 FPS synthetic stream keeps ~20%.
- Job completes on file EOF.

TESTS:
- Sampler unit; ingest job with Dummy callback.

DO NOT:
- Do not run detection in this TODO (hook only).
- Do not add Kafka.

---

## PHASE 5 — AI Detection

### TODO VR-030 — Detector protocol and DummyDetector

OBJECTIVE:
Deterministic detections for tests and GPU-less demos.

FILES TO CREATE:
- `backend/app/vision/detector_base.py`
- `backend/app/vision/dummy_detector.py`
- `backend/app/vision/types.py`
- `backend/tests/unit/test_dummy_detector.py`

FILES TO MODIFY:
- `backend/app/pipeline/runner.py` — optional detect callback still unused until VR-033

IMPLEMENTATION:
```python
@dataclass
class DetectionCandidate:
    class_name: str  # person|vehicle|animal|fire|smoke|unknown
    class_id: int
    confidence: float  # 0-1
    bbox_xyxy: tuple[float,float,float,float]
    detector_id: str
    model_version: str

class Detector(Protocol):
    def detect(self, frame: Frame) -> list[DetectionCandidate]: ...
```
`DummyDetector` reads optional `script` of timed boxes or paints based on seq (e.g. seq 10–50 emit person). Never sets class_name to forbidden terms.

INTERFACES / CONTRACTS:
`DetectionCandidate` is the only detection payload entering persistence.

DEPENDENCIES:
VR-025, VR-002

INPUTS:
Frame.

OUTPUTS:
Detections in memory.

ACCEPTANCE CRITERIA:
- Dummy is deterministic given seq.
- Classes limited to taxonomy.

TESTS:
- Fixed frames → exact boxes.

DO NOT:
- Do not load ONNX here.
- Do not write incidents.

---

### TODO VR-031 — ONNX YOLOX (or equivalent Apache) detector adapter

OBJECTIVE:
Real pretrained inference path without default AGPL.

FILES TO CREATE:
- `backend/app/vision/onnx_detector.py`
- `backend/app/vision/taxonomy.py` — map COCO ids to vanraksha classes
- `models/README.md`
- `backend/tests/unit/test_taxonomy.py`
- `backend/tests/unit/test_onnx_detector.py` — skip if no weights

FILES TO MODIFY:
- `scripts/download_models.py` — document URL; do not violate licenses
- `config/license_policy.yaml` if a package added
- `docs/THIRD_PARTY_LICENSES.md` — fill actual model once chosen

IMPLEMENTATION:
Load ONNX with onnxruntime CPU. Preprocess as required by chosen model. Map: person→person, car/truck/bus/motorcycle→vehicle, bird/cat/dog/horse/sheep/cow/elephant/bear/zebra/giraffe→animal, if model has fire/smoke use them else leave for Dummy/fire TODO. If weights missing, factory falls back to DummyDetector when `demo_mode` else raise.

INTERFACES / CONTRACTS:
`OnnxDetector(weights_path, providers=['CPUExecutionProvider'])` implements Detector.  
`map_class(coco_name: str) -> str | None` (None = drop class).

DEPENDENCIES:
VR-030, VR-004

INPUTS:
ONNX file optional.

OUTPUTS:
Production detector adapter.

ACCEPTANCE CRITERIA:
- Importing onnx_detector does not import ultralytics.
- Taxonomy drops furniture/irrelevant COCO classes.

TESTS:
- Taxonomy unit tests.
- ONNX test skipif not exists.

DO NOT:
- Do not add `ultralytics` to default deps.
- Do not train a model.
- Do not claim species-level wildlife ID.

---

### TODO VR-032 — Detection persistence and detections API

OBJECTIVE:
Store and query detections.

FILES TO CREATE:
- `backend/app/services/detection_service.py`
- `backend/app/schemas/detection.py`
- `backend/app/api/v1/detections.py`
- `backend/tests/integration/test_detections_api.py`

FILES TO MODIFY:
- pipeline runner to persist when detector attached (or VR-034)

IMPLEMENTATION:
`GET /api/v1/detections?camera_id&from&to&class_name` paginated. No public POST from clients (pipeline-only service function `persist_detections`).

INTERFACES / CONTRACTS:
`DetectionRead` includes confidence, bbox, captured_at, **not** risk.

DEPENDENCIES:
VR-016, VR-030, VR-020

INPUTS:
DetectionCandidate.

OUTPUTS:
DB + API.

ACCEPTANCE CRITERIA:
- Query by time range.
- Confidence stored.

TESTS:
- Insert via service; GET list.

DO NOT:
- Do not expose a public unauthenticated upload of fake “poacher” labels.

---

### TODO VR-033 — Wire detector into pipeline runner

OBJECTIVE:
End-to-end frame → detections in worker.

FILES TO CREATE:
- `backend/app/vision/factory.py` — `build_detector(settings) -> Detector`
- `backend/tests/integration/test_pipeline_detect.py`

FILES TO MODIFY:
- `backend/app/pipeline/runner.py`
- `backend/app/core/config.py` — `detector_backend: dummy|onnx`

IMPLEMENTATION:
After sampler, call detector.detect; persist. Update camera_health.last_detection_at if any. Log FPS.

INTERFACES / CONTRACTS:
Runner config: detector from factory.

DEPENDENCIES:
VR-029, VR-032, VR-031

INPUTS:
Ingest job.

OUTPUTS:
Detections during file ingest.

ACCEPTANCE CRITERIA:
- File ingest with DummyDetector creates detection rows.

TESTS:
- Integration: synthetic video + DummyDetector → count>0.

DO NOT:
- Do not add tracking yet.
- Do not open incidents.

---

### TODO VR-034 — Class taxonomy display mapping in API

OBJECTIVE:
API/UI labels use catalog, not raw COCO names.

FILES TO CREATE:
- `backend/app/schemas/taxonomy.py`
- `backend/app/api/v1/taxonomy.py`
- `backend/tests/unit/test_taxonomy_api.py`

FILES TO MODIFY:
- `config/language_catalog.yaml` if needed

IMPLEMENTATION:
`GET /api/v1/taxonomy` returns classes with `display_name`, `language_key`, `layer: detection`.

INTERFACES / CONTRACTS:
Stable class_name strings: person, vehicle, animal, fire, smoke, unknown.

DEPENDENCIES:
VR-002, VR-031

INPUTS:
taxonomy.py

OUTPUTS:
Taxonomy API for frontend.

ACCEPTANCE CRITERIA:
- No forbidden terms in display names.

TESTS:
- GET taxonomy; assert_copy_allowed each string.

DO NOT:
- Do not add “weapon” unless a reliable class exists (it does not in MVP).

---

## PHASE 6 — Object Tracking

### TODO VR-035 — Tracker protocol and IoU tracker (MVP fallback)

OBJECTIVE:
Stable IDs without ByteTrack dependency in unit tests.

FILES TO CREATE:
- `backend/app/vision/tracker_base.py`
- `backend/app/vision/iou_tracker.py`
- `backend/tests/unit/test_iou_tracker.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
```python
@dataclass
class TrackUpdate:
    track_id: int
    class_name: str
    confidence: float
    bbox_xyxy: tuple[...]
    centroid: tuple[float,float]
    first_seen: datetime
    last_seen: datetime
    camera_id: UUID

class Tracker(Protocol):
    def update(self, frame: Frame, detections: list[DetectionCandidate]) -> list[TrackUpdate]: ...
```
IoU matcher greedy; max_age in frames; class-aware match.

INTERFACES / CONTRACTS:
`TrackUpdate` as above. `global_id` not set.

DEPENDENCIES:
VR-030

INPUTS:
Detections per frame.

OUTPUTS:
Tracks in memory.

ACCEPTANCE CRITERIA:
- Same box moving slowly keeps id.
- Disappeared tracks expire.

TESTS:
- Synthetic moving bbox identity persistence.

DO NOT:
- Do not implement ReID embeddings.

---

### TODO VR-036 — ByteTrack adapter (MIT)

OBJECTIVE:
Production tracker using MIT ByteTrack (vendored minimal or well-licensed port).

FILES TO CREATE:
- `backend/app/vision/bytetrack_tracker.py`
- `backend/tests/unit/test_bytetrack_tracker.py`

FILES TO MODIFY:
- `docs/THIRD_PARTY_LICENSES.md`
- `pyproject.toml` — only MIT-licensed implementation; if you vendor ByteTrack files, keep license headers
- `config/license_policy.yaml`

IMPLEMENTATION:
Wrap ByteTrack. If dependency is AGPL (BoxMOT), **stop and use vendored MIT ByteTrack instead**. Factory `tracker_backend: iou|bytetrack`.

INTERFACES / CONTRACTS:
Implements Tracker; emits same TrackUpdate.

DEPENDENCIES:
VR-035, VR-004

INPUTS:
Detections.

OUTPUTS:
ByteTrack-backed Tracker.

ACCEPTANCE CRITERIA:
- No boxmot/ultralytics import.
- LICENSE file of vendored code present.

TESTS:
- Similar to IoU with noisier boxes if possible; at least constructs and updates.

DO NOT:
- Do not add BoxMOT.
- Do not do multi-camera association.

---

### TODO VR-037 — Track persistence and tracks API

OBJECTIVE:
Store tracks and polylines of track_points.

FILES TO CREATE:
- `backend/app/services/track_service.py`
- `backend/app/schemas/track.py`
- `backend/app/api/v1/tracks.py`
- `backend/tests/integration/test_tracks_api.py`

FILES TO MODIFY:
- pipeline runner

IMPLEMENTATION:
Upsert track by (camera_id, local_track_id). Append track_points.  
`GET /api/v1/tracks?camera_id&active=true`  
`GET /api/v1/tracks/{id}/points`

INTERFACES / CONTRACTS:
`TrackRead` with first_seen, last_seen, class_name.

DEPENDENCIES:
VR-016, VR-035

INPUTS:
TrackUpdate.

OUTPUTS:
Tracks API.

ACCEPTANCE CRITERIA:
- Points ordered by time.

TESTS:
- Persist two updates; GET points len=2.

DO NOT:
- Do not compute risk on tracks.

---

### TODO VR-038 — Wire tracker into pipeline

OBJECTIVE:
detect → track → persist in one runner path.

FILES TO CREATE:
- `backend/app/vision/tracker_factory.py`
- `backend/tests/integration/test_pipeline_track.py`

FILES TO MODIFY:
- `backend/app/pipeline/runner.py`

IMPLEMENTATION:
Order: sample → detect → track → persist both. Detection.track_id set when matched.

INTERFACES / CONTRACTS:
Pipeline produces both tables populated.

DEPENDENCIES:
VR-033, VR-037, VR-036

INPUTS:
Ingest job.

OUTPUTS:
Linked detections and tracks.

ACCEPTANCE CRITERIA:
- Dummy person over N frames → one track_id reused.

TESTS:
- Integration synthetic.

DO NOT:
- Do not correlate events yet.

---

## PHASE 7 — Context & Geospatial Intelligence

### TODO VR-039 — SceneContext and ContextProvider

OBJECTIVE:
Attach operational context without changing detectors.

FILES TO CREATE:
- `backend/app/engines/context.py`
- `backend/app/schemas/context.py`
- `backend/tests/geo/test_context_provider.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
```python
@dataclass
class SceneContext:
    camera_id: UUID
    timestamp: datetime
    zone_ids: list[UUID]
    in_restricted: bool
    is_night: bool
    nearby_ranger_ids: list[UUID]
    nearby_wildlife_track_ids: list[UUID]
    camera_online: bool

class ContextProvider(Protocol):
    def for_camera(self, camera_id: UUID, timestamp: datetime) -> SceneContext: ...
```
Night from settings `night_start`, `night_end`, timezone. Restricted via ST_Contains camera point (MVP: **camera location** not object GPS). Document this limitation. Nearby rangers: ST_DWithin radius_m configurable default 500. Wildlife tracks: animal class last_seen within T seconds and same camera (MVP same-camera).

INTERFACES / CONTRACTS:
`SceneContext` consumed by EventEngine.

DEPENDENCIES:
VR-015, VR-018, VR-024

INPUTS:
DB + timestamp.

OUTPUTS:
Context object.

ACCEPTANCE CRITERIA:
- Camera in restricted polygon → in_restricted True.
- Daytime fixture → is_night False.

TESTS:
- Geo tests with seed-like polygons.

DO NOT:
- Do not infer intent.
- Do not use homography unless cameras have calibration (they do not).

---

### TODO VR-040 — Homography-optional object map point (MVP skip with hook)

OBJECTIVE:
Document and stub object-level GIS without fake accuracy.

FILES TO CREATE:
- `backend/app/engines/georef.py`
- `backend/tests/unit/test_georef.py`

FILES TO MODIFY:
- `docs/ARCHITECTURE.md` — MVP uses camera point for zone membership

IMPLEMENTATION:
`estimate_map_point(camera, bbox) -> Point | None` returns None in MVP. Future: calibration JSON on camera.extra_json.

INTERFACES / CONTRACTS:
Always-nullable map_point.

DEPENDENCIES:
VR-039

INPUTS:
Camera, bbox.

OUTPUTS:
None in MVP.

ACCEPTANCE CRITERIA:
- Function returns None; docstring explains why.

TESTS:
- Returns None.

DO NOT:
- Do not pretend bbox center is GPS.

---

### TODO VR-041 — Authorized ranger presence helper

OBJECTIVE:
Risk will subtract when a known ranger is near the camera.

FILES TO CREATE:
- `backend/app/engines/ranger_presence.py`
- `backend/tests/geo/test_ranger_presence.py`

FILES TO MODIFY:
- ContextProvider to fill nearby_ranger_ids (if not complete in VR-039, finish here)

IMPLEMENTATION:
`rangers_near_camera(camera_id, at, radius_m) -> list[UUID]` using latest ranger_locations per ranger (distinct on ranger_id order by captured_at desc) within time_skew 15 min.

INTERFACES / CONTRACTS:
Used as risk factor `authorized_ranger`.

DEPENDENCIES:
VR-039, VR-023

INPUTS:
ranger_locations.

OUTPUTS:
IDs.

ACCEPTANCE CRITERIA:
- Ranger 100m away included; 10km excluded.

TESTS:
- Geo DWithin.

DO NOT:
- Do not auto-clear incidents because a ranger is near (only score delta).

---

## PHASE 8 — Event Engine

### TODO VR-042 — Event type catalog and EventCandidate

OBJECTIVE:
Typed events with language keys only.

FILES TO CREATE:
- `backend/app/engines/event_types.py`
- `backend/app/engines/event_candidate.py`
- `backend/tests/unit/test_event_types.py`

FILES TO MODIFY:
- `config/language_catalog.yaml` if missing keys

IMPLEMENTATION:
Enum EventType matching language keys. `EventCandidate` dataclass: event_type, language_key, track_ids, detection_ids, window_start/end, camera_id, correlation_key, geometry.

INTERFACES / CONTRACTS:
correlation_key format: `{camera_id}:{event_family}:{bucket_epoch}` where bucket is 2-minute window (configurable).

DEPENDENCIES:
VR-002, VR-017

INPUTS:
Catalog.

OUTPUTS:
Types for engine.

ACCEPTANCE CRITERIA:
- All EventType values have catalog messages.
- Forbidden terms test passes.

TESTS:
- Catalog completeness.

DO NOT:
- Do not add EventType.POACHER.

---

### TODO VR-043 — EventEngine.evaluate_track_window

OBJECTIVE:
Turn tracks + context into candidates (pre-correlation).

FILES TO CREATE:
- `backend/app/engines/event_engine.py`
- `backend/tests/unit/test_event_engine.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
Rules (MVP):
- person track active → candidate `person_detected` (may be suppressed later)
- vehicle → `vehicle_detected`
- animal → `animal_detected` / wildlife observation hook
- fire/smoke classes → fire events
- person + in_restricted → `restricted_zone_activity`
- person + is_night → flag on candidate payload
Do not emit five user alerts; mark `alertable: False` on raw detections; `alertable: True` only for suspicious/fire/sos/health. Raw detections still stored as events with `alertable False` OR skip persisting raw and only persist operational events — **choose: persist operational events only**: restricted_zone_activity, suspicious_activity, fire, smoke, wildlife_unusual_movement, camera_*. Person-only in public zone daytime is NOT an incident.

INTERFACES / CONTRACTS:
`EventEngine.evaluate(tracks: list[TrackUpdate], ctx: SceneContext) -> list[EventCandidate]`

DEPENDENCIES:
VR-042, VR-039, VR-038

INPUTS:
Tracks + context.

OUTPUTS:
Candidates.

ACCEPTANCE CRITERIA:
- Daytime person outside restricted → no alertable event.
- Night + restricted + person → alertable suspicious or restricted event.

TESTS:
- Table-driven tests for the two cases above + vehicle+person+restricted.

DO NOT:
- Do not score risk here (RiskEngine).
- Do not write “poacher”.

---

### TODO VR-044 — Correlation, grouping, duplicate suppression

OBJECTIVE:
Multiple signals → one correlated incident-worthy event.

FILES TO CREATE:
- `backend/app/engines/correlation.py`
- `backend/tests/unit/test_correlation.py`

FILES TO MODIFY:
- `event_engine.py` — call correlator

IMPLEMENTATION:
Same correlation_key within window merges person+vehicle+restricted+night+wildlife_nearby into one `suspicious_activity` (or `_high_risk` placeholder before risk). Duplicate suppression: if same correlation_key event exists in last N minutes, update payload instead of insert. Spatial: same camera_id MVP (cross-camera FUTURE).

INTERFACES / CONTRACTS:
`correlate(candidates) -> list[EventCandidate]` length 1 for the demo combo.

DEPENDENCIES:
VR-043

INPUTS:
Multiple candidates.

OUTPUTS:
Merged candidate.

ACCEPTANCE CRITERIA:
- Five signals → one alertable event.
- Second evaluation 30s later updates not duplicates (service-level test can be VR-045).

TESTS:
- Unit correlate.

DO NOT:
- Do not use ML clustering.

---

### TODO VR-045 — Event persistence and events API

OBJECTIVE:
Store events/factors placeholders and query them.

FILES TO CREATE:
- `backend/app/services/event_service.py`
- `backend/app/schemas/event.py`
- `backend/app/api/v1/events.py`
- `backend/tests/integration/test_events_api.py`

FILES TO MODIFY:
- pipeline runner after tracks: context → engine → persist

IMPLEMENTATION:
`GET /api/v1/events` filters. Upsert by correlation_key. Factors filled in VR-047.

INTERFACES / CONTRACTS:
`EventRead` includes language_key, alertable, correlation_key.

DEPENDENCIES:
VR-044, VR-017

INPUTS:
EventCandidate.

OUTPUTS:
Events API + pipeline hook.

ACCEPTANCE CRITERIA:
- Pipeline on dummy restricted night script creates one event not five.

TESTS:
- Integration with DummyDetector script + seed restricted camera + frozen night timestamp.

DO NOT:
- Do not notify yet (VR-067).

---

## PHASE 9 — Risk Engine

### TODO VR-046 — Risk factor configuration

OBJECTIVE:
Configurable deterministic weights, not scattered magic numbers.

FILES TO CREATE:
- `backend/app/engines/risk_defaults.py`
- `backend/alembic` data seed in settings OR seed_demo update
- `backend/tests/unit/test_risk_defaults.py`

FILES TO MODIFY:
- `scripts/seed_demo.py` — upsert `risk_weights`
- `backend/app/api/v1/settings.py` — validate schema on PUT key risk_weights

IMPLEMENTATION:
Default JSON:
```json
{
  "max_score": 100,
  "levels": {"low": [0,30], "medium": [31,60], "high": [61,80], "critical": [81,100]},
  "factors": [
    {"code": "restricted_zone", "delta": 25},
    {"code": "nighttime", "delta": 10},
    {"code": "vehicle", "delta": 15},
    {"code": "suspicious_pattern", "delta": 25},
    {"code": "wildlife_nearby", "delta": 15},
    {"code": "repeated_movement", "delta": 10},
    {"code": "camera_tampering", "delta": 20},
    {"code": "authorized_ranger", "delta": -40}
  ]
}
```
Clamp 0–100.

INTERFACES / CONTRACTS:
`RiskWeights` pydantic model. DB overrides file defaults.

DEPENDENCIES:
VR-024, VR-019

INPUTS:
Settings.

OUTPUTS:
Weights document.

ACCEPTANCE CRITERIA:
- PUT invalid level ranges 422.
- Defaults match placeholders (tunable).

TESTS:
- Schema validation tests.

DO NOT:
- Do not train ML.
- Do not hardcode deltas in EventEngine.

---

### TODO VR-047 — RiskEngine.score with explanations

OBJECTIVE:
Every score has WHY.

FILES TO CREATE:
- `backend/app/engines/risk_engine.py`
- `backend/tests/unit/test_risk_engine.py`

FILES TO MODIFY:
- event_service persist factors

IMPLEMENTATION:
```python
@dataclass
class RiskFactorHit:
    code: str
    delta: int
    reason: str

@dataclass
class RiskAssessment:
    score: int
    level: RiskLevel
    factors: list[RiskFactorHit]
    requires_human_verification: bool  # True if level HIGH or CRITICAL
```
`RiskEngine.score(event: EventCandidate, ctx: SceneContext, extras: dict) -> RiskAssessment`  
Apply matching factors; build reasons in English from templates (not accusations). `repeated_movement` if same camera person tracks ≥3 in 30 min (query). Clamp. Always attach factors list even if empty.

INTERFACES / CONTRACTS:
Persisted as event.risk_score + event_factors rows.

DEPENDENCIES:
VR-046, VR-045, VR-041

INPUTS:
Event + context + weights.

OUTPUTS:
RiskAssessment.

ACCEPTANCE CRITERIA:
- Restricted+night+vehicle example produces documented factor codes and score 25+10+15=50 MEDIUM (plus others if present).
- HIGH/CRITICAL set requires_human_verification.

TESTS:
- Golden tests for score math; ranger presence negative delta.

DO NOT:
- Do not output “poacher probability”.
- Do not hide negative factors.

---

### TODO VR-048 — Risk preview API

OBJECTIVE:
Allow officers to see weights and a dry-run explanation.

FILES TO CREATE:
- `backend/app/api/v1/risk.py`
- `backend/app/schemas/risk.py`
- `backend/tests/integration/test_risk_api.py`

FILES TO MODIFY:
- router

IMPLEMENTATION:
`GET /api/v1/risk/weights`  
`POST /api/v1/risk/preview` with flags → assessment JSON (ADMIN/FOREST_OFFICER later).

INTERFACES / CONTRACTS:
Preview uses same RiskEngine (no duplicate math).

DEPENDENCIES:
VR-047

INPUTS:
Flags.

OUTPUTS:
Explainable JSON.

ACCEPTANCE CRITERIA:
- Preview matches engine unit golden case.

TESTS:
- API golden.

DO NOT:
- Do not expose a public unauthenticated tuner on production without auth (comment VR-083).

---

## PHASE 10 — Incident Management

### TODO VR-049 — Incident state machine

OBJECTIVE:
Explicit legal-ish operational lifecycle in one module.

FILES TO CREATE:
- `backend/app/engines/incident_state.py`
- `backend/tests/unit/test_incident_state.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
Allowed transitions:
NEW→ACKNOWLEDGED, NEW→INVESTIGATING  
ACKNOWLEDGED→INVESTIGATING, ACKNOWLEDGED→DISPATCHED  
INVESTIGATING→DISPATCHED, INVESTIGATING→RESOLVED  
DISPATCHED→INVESTIGATING, DISPATCHED→RESOLVED  
RESOLVED→CLOSED, RESOLVED→INVESTIGATING  
CLOSED→ none (except ADMIN reopen CLOSED→INVESTIGATING)  
Invalid raises AppError.

INTERFACES / CONTRACTS:
`can_transition(src, dst, role) -> bool`  
`transition(...)`

DEPENDENCIES:
VR-017

INPUTS:
Enums.

OUTPUTS:
State machine.

ACCEPTANCE CRITERIA:
- Invalid transition tested.
- VIEWER cannot transition (role arg).

TESTS:
- Parametrized transitions.

DO NOT:
- Do not auto-CLOSED on timeout in MVP.

---

### TODO VR-050 — IncidentManager upsert from events

OBJECTIVE:
Create or attach incidents for alertable events.

FILES TO CREATE:
- `backend/app/engines/incident_manager.py`
- `backend/tests/unit/test_incident_manager.py`

FILES TO MODIFY:
- pipeline after risk

IMPLEMENTATION:
If event.alertable and risk.level >= MEDIUM (configurable `incident_min_level`): create incident or attach to open incident with same correlation_key family. Title from language catalog. public_id sequential. Write status history NEW. Assign none.

INTERFACES / CONTRACTS:
`IncidentManager.upsert_from_event(event, risk) -> Incident`

DEPENDENCIES:
VR-049, VR-047, VR-045

INPUTS:
Scored events.

OUTPUTS:
Incidents.

ACCEPTANCE CRITERIA:
- Duplicate correlation_key does not create second OPEN incident.
- LOW person noise does not create incident.

TESTS:
- Unit with fakes.

DO NOT:
- Do not auto-dispatch rangers.

---

### TODO VR-051 — Incident API (CRUD-lite + lifecycle)

OBJECTIVE:
Command Centre backend for incidents.

FILES TO CREATE:
- `backend/app/schemas/incident.py`
- `backend/app/services/incident_service.py`
- `backend/app/api/v1/incidents.py`
- `backend/tests/integration/test_incidents_api.py`

FILES TO MODIFY:
- router

IMPLEMENTATION:
`GET /api/v1/incidents` filter status, level, camera, from/to  
`GET /api/v1/incidents/{id}` includes events, factors, evidence ids  
`POST /api/v1/incidents/{id}/transition {to_status, note}`  
`POST /api/v1/incidents/{id}/assign {user_id|ranger_id}`  
`POST /api/v1/incidents/{id}/notes`

INTERFACES / CONTRACTS:
`IncidentDetail` nested.

DEPENDENCIES:
VR-050, VR-020

INPUTS:
Incidents table.

OUTPUTS:
Incident API.

ACCEPTANCE CRITERIA:
- Transition writes history.
- List pagination.

TESTS:
- Create via manager in test; transition ACKNOWLEDGED.

DO NOT:
- Do not delete incidents; no hard delete endpoint.

---

### TODO VR-052 — Incident audit history API

OBJECTIVE:
Immutable-enough history listing.

FILES TO CREATE:
- (may be part of VR-051; if missing) `GET /api/v1/incidents/{id}/history`

FILES TO MODIFY:
- incident router/schemas

IMPLEMENTATION:
Return status_history ordered. Audit_logs entry on transition (actor nullable until auth).

INTERFACES / CONTRACTS:
`StatusHistoryRead`.

DEPENDENCIES:
VR-051, VR-018

INPUTS:
history table.

OUTPUTS:
History JSON.

ACCEPTANCE CRITERIA:
- Order chronological.

TESTS:
- Two transitions → two history rows.

DO NOT:
- Do not allow PATCH of history rows.

---

## PHASE 11 — Evidence Management

### TODO VR-053 — EvidenceStore protocol and local hashed store

OBJECTIVE:
Store frames with SHA-256; no legal-grade claims.

FILES TO CREATE:
- `backend/app/evidence/base.py`
- `backend/app/evidence/local_store.py`
- `backend/tests/unit/test_local_evidence_store.py`

FILES TO MODIFY:
- `.gitignore` evidence blobs
- settings `evidence_dir`

IMPLEMENTATION:
```python
class EvidenceStore(Protocol):
    def put_bytes(self, data: bytes, *, suffix: str) -> EvidenceRef: ...
class EvidenceRef:
    sha256: str
    storage_uri: str  # file:// relative
    nbytes: int
```
Write to `evidence_dir/ab/cd/{sha256}.jpg`. Verify hash on read. Path traversal tests.

INTERFACES / CONTRACTS:
`EvidenceRef`. Disclaimer not stored as “admissible”.

DEPENDENCIES:
VR-017, VR-007

INPUTS:
Bytes.

OUTPUTS:
Files + hash.

ACCEPTANCE CRITERIA:
- Duplicate put same hash.
- `../` names rejected.

TESTS:
- Hash stability; traversal reject.

DO NOT:
- Do not upload to paid S3.
- Do not label “court admissible”.

---

### TODO VR-054 — Capture pipeline (annotated frame)

OBJECTIVE:
On alertable event, save JPEG with bbox overlay + metadata JSON sidecar optional.

FILES TO CREATE:
- `backend/app/evidence/capture.py`
- `backend/tests/unit/test_capture.py`

FILES TO MODIFY:
- pipeline after incident upsert

IMPLEMENTATION:
Draw bbox and class_name+confidence (not risk accusation). Persist evidence row linked to incident/event. Overlay must not include forbidden terms.

INTERFACES / CONTRACTS:
`capture_frame(frame, tracks, event, incident) -> Evidence`

DEPENDENCIES:
VR-053, VR-050, VR-002

INPUTS:
Frame + boxes.

OUTPUTS:
Evidence rows.

ACCEPTANCE CRITERIA:
- File exists; sha256 matches file.
- JPEG readable by OpenCV.

TESTS:
- Dummy black frame + box.

DO NOT:
- Do not store full MP4 clips in MVP (ADVANCED).

---

### TODO VR-055 — Evidence API and access logging

OBJECTIVE:
Fetch evidence metadata; stream file with audit.

FILES TO CREATE:
- `backend/app/schemas/evidence.py`
- `backend/app/api/v1/evidence.py`
- `backend/app/services/evidence_service.py`
- `backend/tests/integration/test_evidence_api.py`

FILES TO MODIFY:
- audit service helper

IMPLEMENTATION:
`GET /api/v1/evidence/{id}` metadata including disclaimer text from catalog.  
`GET /api/v1/evidence/{id}/file` image. Log audit `EVIDENCE_READ`. VIEWER may be denied file in VR-085; for now allow + comment.

INTERFACES / CONTRACTS:
Metadata includes `disclaimer`.

DEPENDENCIES:
VR-054, VR-018

INPUTS:
Evidence id.

OUTPUTS:
API.

ACCEPTANCE CRITERIA:
- Disclaimer present.
- 404 unknown id.

TESTS:
- Create evidence; GET file 200 image/jpeg.

DO NOT:
- Do not add public unguessable-only security without auth (add note for VR-083).

---

## PHASE 12 — Wildlife Intelligence

### TODO VR-056 — Wildlife observations API

OBJECTIVE:
Store animal tracks as observations without species certainty.

FILES TO CREATE:
- `backend/app/models/wildlife.py` + alembic if new table `wildlife_observations`
- `backend/app/schemas/wildlife.py`
- `backend/app/services/wildlife_service.py`
- `backend/app/api/v1/wildlife.py`
- `backend/tests/integration/test_wildlife_api.py`

FILES TO MODIFY:
- pipeline when class_name==animal

IMPLEMENTATION:
Observation: track_id, camera_id, species=`unknown`, count_estimate=1, first_seen, last_seen, location=camera point. `GET /api/v1/wildlife/observations`.

INTERFACES / CONTRACTS:
species default unknown. Display: “Animal detected (species unverified).”

DEPENDENCIES:
VR-038, VR-002, VR-015

INPUTS:
Animal tracks.

OUTPUTS:
Wildlife API.

ACCEPTANCE CRITERIA:
- No species invented.
- List filter by camera.

TESTS:
- Persist from animal dummy class.

DO NOT:
- Do not claim MegaDetector accuracy until adapter exists.
- Do not explain *why* animals moved.

---

### TODO VR-057 — SpeciesClassifier protocol + optional MegaDetector adapter stub

OBJECTIVE:
Architecture for species ID without requiring it.

FILES TO CREATE:
- `backend/app/vision/species.py`
- `backend/tests/unit/test_species_stub.py`

FILES TO MODIFY:
- `docs/THIRD_PARTY_LICENSES.md` — MegaDetector optional
- wildlife_service to call classifier if configured

IMPLEMENTATION:
```python
class SpeciesClassifier(Protocol):
    def classify(self, crop_bgr) -> SpeciesResult  # label, confidence, unverified: bool
```
`NullSpeciesClassifier` always unknown. `MegaDetectorAdapter` raises NotImplemented or skip unless weights and license OK (ADVANCED). Config `species_backend: null|megadetector`.

INTERFACES / CONTRACTS:
Never set unverified False unless confidence ≥ threshold AND model present.

DEPENDENCIES:
VR-056, VR-004

INPUTS:
Crops.

OUTPUTS:
Stub classifier.

ACCEPTANCE CRITERIA:
- Default unknown.
- Code path documented.

TESTS:
- Null classifier.

DO NOT:
- Do not download MegaDetector in MVP CI.
- Do not enable by default.

---

### TODO VR-058 — Simple wildlife movement anomaly

OBJECTIVE:
Heuristic unusual movement; verification language only.

FILES TO CREATE:
- `backend/app/engines/wildlife_anomaly.py`
- `backend/tests/unit/test_wildlife_anomaly.py`

FILES TO MODIFY:
- EventEngine to emit `wildlife_unusual_movement` if anomaly and animal track

IMPLEMENTATION:
MVP rules (any one): speed in image px/s above threshold; appears in ≥3 cameras N/A (single camera): track length > T minutes; revisit same camera 5 times in 1h. Emit event language from catalog. No causal text.

INTERFACES / CONTRACTS:
`is_anomalous(track_points) -> bool, reason_code`

DEPENDENCIES:
VR-043, VR-056

INPUTS:
track_points.

OUTPUTS:
Optional event.

ACCEPTANCE CRITERIA:
- Short static track not anomalous.
- Catalog phrase used.

TESTS:
- Unit heuristics.

DO NOT:
- Do not say “fleeing from poachers”.

---

## PHASE 13 — Fire Intelligence

### TODO VR-059 — Fire/smoke event mapping and severity heuristic

OBJECTIVE:
Map fire/smoke detections to operational events without spread physics.

FILES TO CREATE:
- `backend/app/engines/fire.py`
- `backend/tests/unit/test_fire_engine.py`

FILES TO MODIFY:
- EventEngine / pipeline

IMPLEMENTATION:
If class fire or smoke: alertable event `fire_detected`/`smoke_detected`. Severity MVP: `low` if smoke only conf<0.5; `medium` smoke; `high` fire class; `critical` fire + multiple cameras (FUTURE skip). Attach nearby rangers via ContextProvider. `spread_prediction: null` always in MVP with field present.

INTERFACES / CONTRACTS:
`FireAssessment { severity, nearby_ranger_ids, spread_prediction: None }`.

DEPENDENCIES:
VR-043, VR-041

INPUTS:
Detections.

OUTPUTS:
Fire events.

ACCEPTANCE CRITERIA:
- `spread_prediction` is JSON null.
- Dummy fire class creates incident-capable event.

TESTS:
- Unit mapping.

DO NOT:
- Do not implement Rothermel or wind spread.
- Do not show animated fire perimeters as scientific.

---

### TODO VR-060 — Fire API and nearby assets

OBJECTIVE:
Query fire events and nearby cameras/rangers.

FILES TO CREATE:
- `backend/app/api/v1/fire.py`
- `backend/app/schemas/fire.py`
- `backend/tests/integration/test_fire_api.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
`GET /api/v1/fire/events`  
`GET /api/v1/fire/events/{id}/nearby` returns rangers and cameras within radius.

INTERFACES / CONTRACTS:
Nearby uses PostGIS DWithin.

DEPENDENCIES:
VR-059, VR-022

INPUTS:
Events type fire/smoke.

OUTPUTS:
Fire API.

ACCEPTANCE CRITERIA:
- nearby empty list ok.

TESTS:
- Seed + dummy event.

DO NOT:
- Do not add satellite hotspots.

---

## PHASE 14 — Ranger Safety

### TODO VR-061 — Simulated GPS ingest and locations API

OBJECTIVE:
LocationProvider with simulated source.

FILES TO CREATE:
- `backend/app/sources/location_base.py`
- `backend/app/services/location_service.py`
- `backend/app/api/v1/locations.py`
- `backend/tests/integration/test_locations_api.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
```python
class LocationProvider(Protocol):
    def ingest(self, ranger_id, point, captured_at, source: str) -> None: ...
    def latest(self) -> list[RangerLocation]: ...
```
`POST /api/v1/rangers/{id}/location {lat,lon,captured_at}` source=simulated. `GET /api/v1/rangers/locations/latest`.

INTERFACES / CONTRACTS:
LocationProvider. GPS device FUTURE uses same ingest.

DEPENDENCIES:
VR-023, VR-018

INPUTS:
Lat/lon.

OUTPUTS:
ranger_locations rows.

ACCEPTANCE CRITERIA:
- Latest per ranger.

TESTS:
- Post two points; latest is newest.

DO NOT:
- Do not require phone app.

---

### TODO VR-062 — SOS flow

OBJECTIVE:
Ranger SOS creates CRITICAL incident + notification language.

FILES TO CREATE:
- `backend/app/services/sos_service.py`
- `backend/app/api/v1/sos.py`
- `backend/tests/integration/test_sos_api.py`

FILES TO MODIFY:
- language catalog `ranger_sos`
- IncidentManager path for SOS (bypass min MEDIUM)

IMPLEMENTATION:
`POST /api/v1/rangers/{id}/sos` → incident language_key ranger_sos, risk 100 CRITICAL, status NEW, capture last location. Always requires_human_verification.

INTERFACES / CONTRACTS:
SOS cannot be created by detector.

DEPENDENCIES:
VR-050, VR-061, VR-002

INPUTS:
Ranger id.

OUTPUTS:
Incident + notification row.

ACCEPTANCE CRITERIA:
- SOS always CRITICAL.
- Copy is safety not accusation.

TESTS:
- POST sos → incident exists.

DO NOT:
- Do not auto-call paid SMS APIs.

---

### TODO VR-063 — Patrols API and inactivity architecture stub

OBJECTIVE:
Patrol records + documented FUTURE inactivity/fall.

FILES TO CREATE:
- `backend/app/api/v1/patrols.py`
- `backend/app/schemas/patrol.py`
- `backend/app/engines/inactivity.py` — stub
- `backend/tests/unit/test_inactivity_stub.py`
- `backend/tests/integration/test_patrols_api.py`

FILES TO MODIFY:
- ARCHITECTURE.md FUTURE wearable

IMPLEMENTATION:
CRUD patrols start/stop. `InactivityMonitor.check(ranger_id) -> None` MVP returns `InactivityResult(active=True, reason="not_implemented")` and does **not** create incidents. Comment how last location age could later flag.

INTERFACES / CONTRACTS:
Stub never emits false fall alerts.

DEPENDENCIES:
VR-061

INPUTS:
Patrol times.

OUTPUTS:
Patrols API + stub.

ACCEPTANCE CRITERIA:
- Stub does not write incidents.
- Patrol start/stop works.

TESTS:
- Stub test; patrol API.

DO NOT:
- Do not fake accelerometer ML.

---

## PHASE 15 — Camera Health

### TODO VR-064 — Heartbeat and online/offline

OBJECTIVE:
Distinguish cameras that check in vs not.

FILES TO CREATE:
- `backend/app/services/health_service.py`
- `backend/app/api/v1/camera_health.py`
- `backend/tests/integration/test_camera_health_api.py`

FILES TO MODIFY:
- ingest runner heartbeat each frame or every 5s
- worker

IMPLEMENTATION:
`CameraHealthMonitor.observe(camera_id, signal: Heartbeat|Frame|Error)`. offline if heartbeat older than `offline_after_seconds` default 30. `GET /api/v1/cameras/health`.

INTERFACES / CONTRACTS:
Protocol CameraHealthMonitor.

DEPENDENCIES:
VR-018, VR-029

INPUTS:
Heartbeats.

OUTPUTS:
Health API.

ACCEPTANCE CRITERIA:
- No heartbeat → offline.
- Running ingest → online.

TESTS:
- Freeze time / manipulate last_heartbeat.

DO NOT:
- Do not treat zero detections as failure (that is VR-065).

---

### TODO VR-065 — Empty scene vs stalled pipeline

OBJECTIVE:
No wildlife/humans ≠ camera dead.

FILES TO CREATE:
- `backend/app/engines/health_logic.py`
- `backend/tests/unit/test_health_logic.py`

FILES TO MODIFY:
- health_service

IMPLEMENTATION:
If frames arriving and detections 0 → state online, notes `no_activity`. If no frames but process expected running → degraded/offline `pipeline_stall`. If job not running and no heartbeat → offline `not_ingesting`.

INTERFACES / CONTRACTS:
`classify_health(last_frame, last_heartbeat, last_detection, job_running) -> (state, reason_code)`

DEPENDENCIES:
VR-064

INPUTS:
Timestamps.

OUTPUTS:
Reason codes.

ACCEPTANCE CRITERIA:
- Frames without detections ≠ failure.

TESTS:
- Four-branch unit tests.

DO NOT:
- Do not alert “camera destroyed” without heuristic.

---

### TODO VR-066 — Tamper / obstruction MVP heuristics

OBJECTIVE:
Weak heuristics labeled as suspected, verification required.

FILES TO CREATE:
- `backend/app/vision/tamper.py`
- `backend/tests/unit/test_tamper.py`

FILES TO MODIFY:
- pipeline optional every K frames
- language catalog camera_tampering_suspected

IMPLEMENTATION:
MVP: mean brightness < threshold for M seconds → obstruction suspected; sudden large pixel MAD vs reference frame → scene_change suspected. Emit alertable event low/medium risk using tamper factor. Always suspected language.

INTERFACES / CONTRACTS:
`TamperHeuristic.result: none|obstruction_suspected|scene_change_suspected`

DEPENDENCIES:
VR-043, VR-002

INPUTS:
Frames.

OUTPUTS:
Optional events.

ACCEPTANCE CRITERIA:
- All-black frames after normal gray trigger obstruction_suspected.
- Copy includes verification.

TESTS:
- Synthetic frames.

DO NOT:
- Do not claim “camera stolen” as fact.
- Do not require extra ML model.

---

## PHASE 16 — Real-Time Communication

### TODO VR-067 — WebSocket hub

OBJECTIVE:
Push incidents, health, SOS to Command Centre.

FILES TO CREATE:
- `backend/app/ws/hub.py`
- `backend/app/api/v1/ws.py`
- `backend/tests/integration/test_ws.py`

FILES TO MODIFY:
- main.py websocket route `/api/v1/ws`

IMPLEMENTATION:
In-memory Hub `broadcast(topic, json)`. Topics: `incidents`, `health`, `sos`, `events`. MVP single-process (document: multiple API replicas need ADVANCED pubsub). Auth query token later.

INTERFACES / CONTRACTS:
Message `{topic, type, payload, ts}`.

DEPENDENCIES:
VR-006

INPUTS:
JSON events.

OUTPUTS:
WS connections.

ACCEPTANCE CRITERIA:
- Two clients receive broadcast.

TESTS:
- Starlette websocket test.

DO NOT:
- Do not add Redis for MVP.
- Do not use Socket.IO if native WS suffices.

---

### TODO VR-068 — Domain publishers

OBJECTIVE:
IncidentManager, health, SOS publish to hub.

FILES TO CREATE:
- `backend/app/notifications/ws_publisher.py`
- `backend/app/notifications/log_provider.py`
- `backend/tests/unit/test_publishers.py`

FILES TO MODIFY:
- IncidentManager, health_service, sos_service

IMPLEMENTATION:
```python
class NotificationProvider(Protocol):
    def notify(self, alert: AlertMessage) -> None: ...
```
`LogNotificationProvider` + `WsNotificationProvider`. Composite. Insert notifications table.

INTERFACES / CONTRACTS:
NotificationProvider. Email/SMS implementations FUTURE no-op class `UnsupportedNotificationProvider`.

DEPENDENCIES:
VR-067, VR-050, VR-062, VR-064

INPUTS:
Domain events.

OUTPUTS:
WS + DB notifications.

ACCEPTANCE CRITERIA:
- Creating incident triggers WS payload with language_key not forbidden terms.

TESTS:
- Mock hub.

DO NOT:
- Do not integrate Twilio.

---

## PHASE 17 — GIS

### TODO VR-069 — GeoJSON APIs

OBJECTIVE:
Map payloads.

FILES TO CREATE:
- `backend/app/api/v1/geo.py`
- `backend/app/schemas/geo.py`
- `backend/tests/geo/test_geojson_api.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
`GET /api/v1/geo/forests|zones|cameras|incidents|rangers|wildlife|fire` as FeatureCollection. Properties include ids and display fields. CRS84.

INTERFACES / CONTRACTS:
RFC 7946 GeoJSON.

DEPENDENCIES:
VR-022, VR-051, VR-056, VR-060, VR-061

INPUTS:
PostGIS.

OUTPUTS:
GeoJSON.

ACCEPTANCE CRITERIA:
- Valid FeatureCollection.
- Restricted zones property `is_restricted`.

TESTS:
- JSON schema-ish asserts type FeatureCollection.

DO NOT:
- Do not proxy Google Maps.

---

### TODO VR-070 — Leaflet map foundation (frontend)

OBJECTIVE:
Full-map Command Centre pane with OSM attribution.

FILES TO CREATE:
- `frontend/src/components/map/ForestMap.tsx`
- `frontend/src/lib/geo.ts`
- `frontend/src/app/command/page.tsx` — or replace home with command layout starting here

FILES TO MODIFY:
- `frontend/package.json` — `leaflet`, `@types/leaflet`; **avoid Hippocratic-licensed bindings** (use leaflet + react useRef)
- `frontend/src/app/globals.css`

IMPLEMENTATION:
Map fills remaining viewport beside a side panel placeholder. OSM tiles + required attribution. Default view from env bbox of demo forest.

INTERFACES / CONTRACTS:
`ForestMap` props: initialCenter, zoom.

DEPENDENCIES:
VR-009, VR-069 (can mock geo until API)

INPUTS:
GeoJSON later.

OUTPUTS:
Map page.

ACCEPTANCE CRITERIA:
- OSM attribution visible.
- No Google keys.

TESTS:
- Component renders in Playwright or RTL if configured; at least build passes.

DO NOT:
- Do not use paid map tiles.

---

### TODO VR-071 — Map layers

OBJECTIVE:
Toggle layers: cameras, zones (restricted styled), incidents, rangers, wildlife, fire.

FILES TO CREATE:
- `frontend/src/components/map/layers/*.tsx`
- `frontend/src/components/map/LayerToggle.tsx`
- `frontend/src/lib/api/geo.ts`

FILES TO MODIFY:
- ForestMap.tsx

IMPLEMENTATION:
Fetch GeoJSON endpoints. Color restricted zones distinctly. Incident markers by risk level color. Click marker → callback `onSelectIncident(id)`.

INTERFACES / CONTRACTS:
Layer ids stable strings.

DEPENDENCIES:
VR-070, VR-069

INPUTS:
API.

OUTPUTS:
Operational map.

ACCEPTANCE CRITERIA:
- Toggles hide/show.
- Restricted vs non-restricted distinguishable.

TESTS:
- Unit test geo parser; e2e later.

DO NOT:
- Do not cluster 100k points (MVP small N).

---

## PHASE 18 — Command Centre Frontend

### TODO VR-072 — Command Centre shell and visual language

OBJECTIVE:
Forest department operations layout: header, left nav, map center, right incident rail.

FILES TO CREATE:
- `frontend/src/components/layout/CommandShell.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/SideNav.tsx`
- `frontend/src/app/command/layout.tsx`

FILES TO MODIFY:
- `page.tsx` redirect to `/command`

IMPLEMENTATION:
Nav items: Overview, Map, Incidents, Cameras, Wildlife, Fire, Rangers, Health, Analytics, Evidence. Professional dense UI, large status pills. Show banner: “AI outputs require human verification.”

INTERFACES / CONTRACTS:
Routes as above (pages can be placeholders).

DEPENDENCIES:
VR-009, VR-002

INPUTS:
None.

OUTPUTS:
Shell.

ACCEPTANCE CRITERIA:
- Verification banner visible.
- Product name visible.

TESTS:
- Playwright smoke navigate `/command`.

DO NOT:
- Do not use generic “Admin Dashboard” copy as the product name.

---

### TODO VR-073 — Typed API client

OBJECTIVE:
Single client for REST.

FILES TO CREATE:
- `frontend/src/lib/api/client.ts`
- `frontend/src/types/api.ts`
- `frontend/src/lib/api/*.ts` modules

FILES TO MODIFY:
- none

IMPLEMENTATION:
fetch wrapper with base URL, error envelope parse. Types for Incident, Event, Camera, RiskAssessment.

INTERFACES / CONTRACTS:
Matches backend schemas; if drift, fix types to backend OpenAPI (can dump later VR-094).

DEPENDENCIES:
VR-051, VR-021 (minimum)

INPUTS:
OpenAPI mentally from routers.

OUTPUTS:
Client.

ACCEPTANCE CRITERIA:
- getIncidents() typed.

TESTS:
- Mock fetch unit test.

DO NOT:
- Do not use untyped `any` for incidents.

---

### TODO VR-074 — Overview widgets

OBJECTIVE:
Counts: open incidents by level, cameras online, rangers, last SOS.

FILES TO CREATE:
- `frontend/src/app/command/page.tsx` overview
- `frontend/src/components/overview/StatCard.tsx`
- `backend/app/api/v1/dashboard.py` — `GET /api/v1/dashboard/summary`

FILES TO MODIFY:
- backend router

IMPLEMENTATION:
Summary SQL counts. UI four+ stats. No fake numbers.

INTERFACES / CONTRACTS:
`DashboardSummary` pydantic.

DEPENDENCIES:
VR-073, VR-051, VR-064

INPUTS:
DB aggregates.

OUTPUTS:
Overview.

ACCEPTANCE CRITERIA:
- Zeros valid.
- Matches DB in integration test.

TESTS:
- API test summary; frontend build.

DO NOT:
- Do not animate fake live random data.

---

### TODO VR-075 — Incident list, filters, detail, actions

OBJECTIVE:
Primary operator workflow.

FILES TO CREATE:
- `frontend/src/app/command/incidents/page.tsx`
- `frontend/src/components/incidents/IncidentList.tsx`
- `frontend/src/components/incidents/IncidentDetail.tsx`
- `frontend/src/components/incidents/RiskBreakdown.tsx`

FILES TO MODIFY:
- map onSelectIncident

IMPLEMENTATION:
List with filters status/level/time. Detail: title from catalog, risk score, **factor list**, related events, assign, transition buttons per state machine, notes. Always show verification if HIGH/CRITICAL.

INTERFACES / CONTRACTS:
Uses IncidentDetail API.

DEPENDENCIES:
VR-051, VR-047, VR-072, VR-073

INPUTS:
Incidents.

OUTPUTS:
Incident UX.

ACCEPTANCE CRITERIA:
- Factors visible.
- Forbidden terms not in UI strings (grep test).

TESTS:
- Playwright: open incident, see factor codes or reasons.
- `test_frontend_copy.spec.ts` grep built strings if possible; at least LANGUAGE keys.

DO NOT:
- Do not add a “Confirm poacher” button.

---

### TODO VR-076 — Camera viewer (file / MJPEG optional)

OBJECTIVE:
Show simulated camera: latest evidence frame or `<video>` of sample file.

FILES TO CREATE:
- `frontend/src/app/command/cameras/page.tsx`
- `frontend/src/components/cameras/CameraViewer.tsx`
- `backend/app/api/v1/cameras_media.py` — `GET /api/v1/cameras/{id}/preview` latest evidence or placeholder

FILES TO MODIFY:
- none

IMPLEMENTATION:
List cameras + status. Viewer: HTML5 video if file URI is a static path served by API in demo_mode (`GET /api/v1/cameras/{id}/stream-file` FileResponse) **only for simulated file sources**. Else show last evidence JPEG.

INTERFACES / CONTRACTS:
Preview endpoint.

DEPENDENCIES:
VR-021, VR-055, VR-026

INPUTS:
Sources.

OUTPUTS:
Camera UX.

ACCEPTANCE CRITERIA:
- Simulated camera can play or show frames without RTSP.

TESTS:
- API returns 404 vs 200 documented.

DO NOT:
- Do not embed paid streaming CDN.

---

### TODO VR-077 — Evidence viewer UI

OBJECTIVE:
Investigate frames with disclaimer.

FILES TO CREATE:
- `frontend/src/components/evidence/EvidenceViewer.tsx`
- `frontend/src/app/command/evidence/page.tsx`

FILES TO MODIFY:
- IncidentDetail

IMPLEMENTATION:
Image, metadata, sha256, disclaimer text exact from catalog. No “legal-grade” badge.

INTERFACES / CONTRACTS:
Evidence metadata API.

DEPENDENCIES:
VR-055, VR-075

INPUTS:
Evidence ids.

OUTPUTS:
Viewer.

ACCEPTANCE CRITERIA:
- Disclaimer visible without scrolling past fold if possible.

TESTS:
- Playwright sees disclaimer substring.

DO NOT:
- Do not add download-all unauthenticated.

---

### TODO VR-078 — Wildlife, fire, ranger, health panels

OBJECTIVE:
Dedicated operational pages (split implementation but one TODO only if small — **implement all four pages** as they are thin list+map-sync).

FILES TO CREATE:
- `frontend/src/app/command/wildlife/page.tsx`
- `frontend/src/app/command/fire/page.tsx`
- `frontend/src/app/command/rangers/page.tsx` — includes SOS button for demo
- `frontend/src/app/command/health/page.tsx`

FILES TO MODIFY:
- SideNav links

IMPLEMENTATION:
Each page: table + status. Ranger page: SOS confirm modal. Health: reason_code empty vs stall. Wildlife: species unverified label. Fire: spread_prediction shown as “Not estimated in MVP”.

INTERFACES / CONTRACTS:
Existing APIs.

DEPENDENCIES:
VR-056, VR-060, VR-062, VR-064, VR-072

INPUTS:
APIs.

OUTPUTS:
Four pages.

ACCEPTANCE CRITERIA:
- Fire page states no spread model.
- Wildlife unverified.

TESTS:
- Smoke Playwright per route 200.

DO NOT:
- Do not add drone telemetry UI.

---

### TODO VR-079 — WebSocket client hook

OBJECTIVE:
Live list updates without refresh.

FILES TO CREATE:
- `frontend/src/lib/ws.ts`
- `frontend/src/hooks/useVanrakshaSocket.ts`

FILES TO MODIFY:
- IncidentList, health page, overview

IMPLEMENTATION:
Reconnect backoff. On `incidents` message, invalidate queries or prepend. Show “LIVE” indicator.

INTERFACES / CONTRACTS:
Same message schema as hub.

DEPENDENCIES:
VR-067, VR-068, VR-075

INPUTS:
WS URL.

OUTPUTS:
Live UI.

ACCEPTANCE CRITERIA:
- New incident appears without full reload (Playwright with dummy WS or backend).

TESTS:
- Prefer integration: API create incident while page open.

DO NOT:
- Do not busy-poll 100ms as the only mechanism (poll fallback 15s OK).

---

### TODO VR-080 — Search and global filters

OBJECTIVE:
Search incidents by public_id, camera name; date range.

FILES TO CREATE:
- `frontend/src/components/filters/GlobalFilters.tsx`

FILES TO MODIFY:
- backend incidents GET query `q=`
- IncidentList

IMPLEMENTATION:
Server-side `q` ilike public_id or title. Date range already on API; wire UI.

INTERFACES / CONTRACTS:
`q` query param.

DEPENDENCIES:
VR-075

INPUTS:
Query string.

OUTPUTS:
Filtered list.

ACCEPTANCE CRITERIA:
- Unknown q → empty not error.

TESTS:
- API q filter test.

DO NOT:
- Do not add Elasticsearch.

---

### TODO VR-081 — Copy/disclaimer component library

OBJECTIVE:
Centralize verification banners.

FILES TO CREATE:
- `frontend/src/components/copy/VerificationBanner.tsx`
- `frontend/src/components/copy/EvidenceDisclaimer.tsx`
- `frontend/src/lib/language.ts` — fetch taxonomy/messages or embed generated JSON from catalog

FILES TO MODIFY:
- layout

IMPLEMENTATION:
Load `language_catalog` via `GET /api/v1/language` (add thin backend endpoint if missing).

INTERFACES / CONTRACTS:
`GET /api/v1/language` returns catalog messages.

DEPENDENCIES:
VR-002, VR-072

INPUTS:
Catalog.

OUTPUTS:
UI copy.

ACCEPTANCE CRITERIA:
- Forbidden terms test on `/api/v1/language`.

TESTS:
- Backend test catalog endpoint.

DO NOT:
- Do not hardcode accusatory strings in JSX.

---

### TODO VR-082 — Historical analytics page (basic)

OBJECTIVE:
Simple charts: incidents per day, by type, by level (7–30 days).

FILES TO CREATE:
- `frontend/src/app/command/analytics/page.tsx`
- `backend/app/api/v1/analytics.py`
- `backend/tests/integration/test_analytics_api.py`

FILES TO MODIFY:
- none

IMPLEMENTATION:
SQL group by date. Frontend: CSS bar tables or simple SVG (no paid chart SaaS). MVP not a data-science lab.

INTERFACES / CONTRACTS:
`GET /api/v1/analytics/incidents?from&to`

DEPENDENCIES:
VR-051, VR-072

INPUTS:
Incidents.

OUTPUTS:
Analytics.

ACCEPTANCE CRITERIA:
- Empty range returns zeros.

TESTS:
- API aggregation.

DO NOT:
- Do not add Jupyter.
- Do not claim predictive poaching hotspots.

---

## PHASE 19 — Authentication & Authorization

### TODO VR-083 — JWT login and password hashing

OBJECTIVE:
Real auth for MVP.

FILES TO CREATE:
- `backend/app/core/security.py` — bcrypt/argon2
- `backend/app/api/v1/auth.py` — login, me
- `backend/app/schemas/auth.py`
- `backend/tests/integration/test_auth.py`

FILES TO MODIFY:
- users seed
- `deps.py` get_current_user

IMPLEMENTATION:
`POST /api/v1/auth/login {email,password}` → access token. Passlib or stdlib hashlib+bcrypt. `GET /api/v1/auth/me`. HTTPS note in docs.

INTERFACES / CONTRACTS:
Bearer JWT. Expiry from settings.

DEPENDENCIES:
VR-014, VR-007

INPUTS:
users.

OUTPUTS:
Auth API.

ACCEPTANCE CRITERIA:
- Wrong password 401.
- Passwords hashed.

TESTS:
- Login success/fail.

DO NOT:
- Do not store JWT secret in git.
- Do not add Google OAuth.

---

### TODO VR-084 — RBAC on all routers

OBJECTIVE:
Enforce roles.

FILES TO CREATE:
- `backend/app/core/rbac.py`
- `backend/tests/integration/test_rbac.py`

FILES TO MODIFY:
- every router

IMPLEMENTATION:
VIEWER: GET most, no evidence file if `restrict_evidence=true` default true, no transitions.  
RANGER: SOS, own location, GET, transition ACK/INVESTIGATING limited.  
FOREST_OFFICER: incidents full except settings.  
ADMIN: settings, users.  
Health live public.  
Document matrix in ARCHITECTURE.md.

INTERFACES / CONTRACTS:
`require_role(*roles)` dependency.

DEPENDENCIES:
VR-083, all APIs

INPUTS:
JWT.

OUTPUTS:
Locked API.

ACCEPTANCE CRITERIA:
- VIEWER cannot PUT settings 403.
- VIEWER cannot POST sos 403.

TESTS:
- Matrix tests.

DO NOT:
- Do not implement ABAC mesh.

---

### TODO VR-085 — Frontend login and route guards

OBJECTIVE:
Login page; attach Bearer; redirect unauthenticated.

FILES TO CREATE:
- `frontend/src/app/login/page.tsx`
- `frontend/src/lib/auth.ts`
- `frontend/src/components/layout/Guards.tsx`

FILES TO MODIFY:
- api client headers
- WS token query

IMPLEMENTATION:
Token in memory + httpOnly cookie **preferred**; if MVP localStorage, document XSS risk. Logout clears.

INTERFACES / CONTRACTS:
Login uses auth API.

DEPENDENCIES:
VR-083, VR-072

INPUTS:
Credentials.

OUTPUTS:
Gated UI.

ACCEPTANCE CRITERIA:
- Unauth `/command` redirects login.
- Login reaches command.

TESTS:
- Playwright login flow with seed user.

DO NOT:
- Do not ship default password in production docs as mandatory.

---

## PHASE 20 — Offline-First / Synchronization

### TODO VR-086 — Edge worker entry

OBJECTIVE:
Run pipeline with EDGE_MODE writing to outbox instead of or in addition to central DB.

FILES TO CREATE:
- `edge/README.md`
- `edge/worker.py`
- `backend/app/sync/outbox.py`
- `backend/tests/unit/test_outbox.py`

FILES TO MODIFY:
- config edge_mode
- docker-compose optional profile `edge`

IMPLEMENTATION:
When EDGE_MODE, persist locally (same Postgres **or** sqlite for outbox-only). MVP: use same DB with `origin=edge` field on events **plus** outbox payloads for demo of queue. Prefer: SQLite outbox file `edge/data/outbox.sqlite` even if detections go sqlite too — keep scope: **outbox records serialized Event+Detection+Incident DTOs**.

INTERFACES / CONTRACTS:
Outbox row idempotency_key.

DEPENDENCIES:
VR-045, VR-050, VR-018

INPUTS:
Pipeline outputs.

OUTPUTS:
Outbox.

ACCEPTANCE CRITERIA:
- EDGE_MODE creates outbox rows.

TESTS:
- Unit enqueue.

DO NOT:
- Do not require physical edge hardware.
- Do not add CRDT complexity.

---

### TODO VR-087 — Sync batch API and deduplication

OBJECTIVE:
Central ingest of edge payloads.

FILES TO CREATE:
- `backend/app/api/v1/sync.py`
- `backend/app/sync/apply.py`
- `backend/tests/integration/test_sync.py`

FILES TO MODIFY:
- rbac: edge device token or ADMIN

IMPLEMENTATION:
`POST /api/v1/sync/batch {items: [{idempotency_key, kind, payload}]}`  
Replay safe. Conflict: first-write-wins on idempotency_key; return `accepted|duplicate`. Dedup also on (camera_id, captured_at, local_track_id, kind).

INTERFACES / CONTRACTS:
Sync item kinds: detection, track, event, incident, evidence_meta (files ADVANCED multipart).

DEPENDENCIES:
VR-086, VR-084

INPUTS:
Outbox JSON.

OUTPUTS:
Upserted rows.

ACCEPTANCE CRITERIA:
- Sending batch twice does not duplicate incidents.

TESTS:
- Double submit.

DO NOT:
- Do not sync raw video blobs in MVP (hashes + later upload ADVANCED).

---

### TODO VR-088 — Offline simulator for demo 7

OBJECTIVE:
Script: run edge with network denied, then sync.

FILES TO CREATE:
- `scripts/demo_offline_sync.py`
- `backend/tests/integration/test_offline_demo.py`

FILES TO MODIFY:
- `docs/DEMO_RUNBOOK.md` (create stub if needed)

IMPLEMENTATION:
Flag `SYNC_URL` empty → queue; then set URL and flush. Test does this in-process.

INTERFACES / CONTRACTS:
Flush function `outbox.flush(client)`.

DEPENDENCIES:
VR-087

INPUTS:
Dummy pipeline.

OUTPUTS:
Demo script.

ACCEPTANCE CRITERIA:
- Test proves incidents appear only after flush.

TESTS:
- Integration test_offline_demo.

DO NOT:
- Do not iptables real network as the only test.

---

## PHASE 21 — Analytics / Learning MVP

### TODO VR-089 — Outcome counters (learn loop MVP)

OBJECTIVE:
When incidents CLOSED, record officer outcome without claiming ML.

FILES TO CREATE:
- `backend/app/models/incident_outcome.py` + alembic
- `backend/app/api/v1/outcomes.py`
- `backend/tests/integration/test_outcomes.py`

FILES TO MODIFY:
- transition to CLOSED requires outcome enum: `confirmed_issue`, `false_positive`, `duplicate`, `training`, `other`

IMPLEMENTATION:
Store outcome. Analytics: false_positive rate last 30d. Display on analytics page. No automatic weight update in MVP (document FUTURE: adjust weights).

INTERFACES / CONTRACTS:
Outcome required on CLOSED.

DEPENDENCIES:
VR-049, VR-082, VR-084

INPUTS:
Officer choice.

OUTPUTS:
Learning data.

ACCEPTANCE CRITERIA:
- Close without outcome 422.
- FP rate API.

TESTS:
- Close flow.

DO NOT:
- Do not auto-retrain YOLO.

---

## PHASE 22 — Testing Pack

### TODO VR-090 — Automated E2E pack for seven demos

OBJECTIVE:
Playwright + pytest integration covering demo scenarios (can use DummyDetector scripts, not real animals).

FILES TO CREATE:
- `backend/tests/e2e_scenarios/test_demo1_suspicious.py`
- `backend/tests/e2e_scenarios/test_demo2_wildlife.py`
- `backend/tests/e2e_scenarios/test_demo3_fire.py`
- `backend/tests/e2e_scenarios/test_demo4_camera.py`
- `backend/tests/e2e_scenarios/test_demo5_sos.py`
- `backend/tests/e2e_scenarios/test_demo6_correlation.py`
- `backend/tests/e2e_scenarios/test_demo7_offline.py`
- `frontend/e2e/command.spec.ts`

FILES TO MODIFY:
- `scripts/seed_demo.py` scenario helpers

IMPLEMENTATION:
Each backend test: seed → scripted DummyDetector → assert incident/event/evidence/language. Demo6: one incident not five. Demo4: stall vs empty. Frontend e2e: login, see incident list. CI can skip GPU.

INTERFACES / CONTRACTS:
Scenario scripts in `backend/app/demo/scripts.py`.

DEPENDENCIES:
VR-088, VR-085, VR-075, all engines

INPUTS:
Dummy timelines.

OUTPUTS:
Test pack.

ACCEPTANCE CRITERIA:
- All seven pytest files pass with DummyDetector.
- At least one Playwright spec passes.

TESTS:
- The files themselves.

DO NOT:
- Do not require live RTSP for CI.
- Do not fail CI if optional ONNX missing.

---

## PHASE 23 — Security & Hardening

### TODO VR-091 — Hardening, threat model, rate limits

OBJECTIVE:
Production-architecture security baseline.

FILES TO CREATE:
- `docs/THREAT_MODEL.md`
- `backend/app/core/rate_limit.py` — in-memory slowapi or custom token bucket per IP
- `backend/tests/unit/test_rate_limit.py`

FILES TO MODIFY:
- CORS settings
- evidence path
- `frontend` security headers in next.config
- optional CI grep for ultralytics if allow_agpl false

IMPLEMENTATION:
Threats: stolen JWT, evidence scrape, RTSP credential leak, model theft, prompt-like log injection, path traversal, insecure demo passwords. Mitigations listed. Rate limit login 5/min/IP. Disable docs in production. Validate uploads (if any) content-type. `SECRET_KEY` min length.

INTERFACES / CONTRACTS:
Rate limiter on `/auth/login`.

DEPENDENCIES:
VR-084, VR-055

INPUTS:
Threat list.

OUTPUTS:
Hardened app + doc.

ACCEPTANCE CRITERIA:
- THREAT_MODEL.md exists.
- Login rate limit test.
- license_policy forbidden packages not in lockfile.

TESTS:
- Rate limit; traversal already in evidence.

DO NOT:
- Do not claim ISO27001 compliance.
- Do not add WAF SaaS requirement.

---

## PHASE 24 — Performance

### TODO VR-092 — Sampling, indexes, metrics endpoint

OBJECTIVE:
MVP performance targets without premature distributed systems.

FILES TO CREATE:
- `backend/app/api/v1/metrics.py` — Prometheus text optional simple counters
- `backend/app/core/metrics.py`
- `backend/tests/unit/test_metrics.py`
- alembic extra indexes if missing

FILES TO MODIFY:
- sampler defaults
- README performance section: MVP 2 FPS 640px CPU; production TBD GPU

IMPLEMENTATION:
Counters: frames_processed, detect_ms, events_created. Indexes already specified; add `incidents(status, created_at)`. Document memory: don’t buffer entire video.

INTERFACES / CONTRACTS:
`GET /api/v1/metrics` (protect ADMIN or scrape localhost).

DEPENDENCIES:
VR-029, VR-051

INPUTS:
Pipeline.

OUTPUTS:
Metrics + notes.

ACCEPTANCE CRITERIA:
- Metrics include detect latency histogram or summary.
- README states MVP FPS target.

TESTS:
- Metrics endpoint contains `frames_processed`.

DO NOT:
- Do not add Kubernetes HPA.
- Do not require GPU for MVP.

---

## PHASE 25 — Demo Scenarios

### TODO VR-093 — Sample assets process and DEMO_RUNBOOK

OBJECTIVE:
SIH operator can run 7 demos without guessing.

FILES TO CREATE:
- `docs/DEMO_RUNBOOK.md`
- `samples/README.md` update
- `backend/app/demo/scripts.py` if not in VR-090
- `scripts/run_demo.ps1`

FILES TO MODIFY:
- seed

IMPLEMENTATION:
For each demo: preconditions, commands, expected UI, fallback DummyDetector, what to say aloud (verification language). How to obtain CC-licensed sample clips (links only, no illegal content, no real crime videos). Camera failure demo: stop worker. Offline demo: VR-088 script.

INTERFACES / CONTRACTS:
Runbook sections DEMO 1–7 matching product request.

DEPENDENCIES:
VR-090, VR-019

INPUTS:
Working system.

OUTPUTS:
Runbook.

ACCEPTANCE CRITERIA:
- Seven sections with expected language_keys.
- Attribution for any sample media.

TESTS:
- Manual checklist in runbook; automated already VR-090.

DO NOT:
- Do not include real poaching footage of people without rights.
- Do not instruct presenters to say “poacher caught”.

---

## PHASE 26 — Documentation

### TODO VR-094 — Operator README and OpenAPI polish

OBJECTIVE:
A stranger can run the stack and understand limitations.

FILES TO CREATE:
- `docs/API.md` — point to `/openapi.json`
- `docs/LIMITATIONS.md` — models, geo, fire, legal

FILES TO MODIFY:
- `README.md` — full: vision, stack, license honesty, demo, env vars
- FastAPI description/tags

IMPLEMENTATION:
Tags on routers. README architecture mermaid optional. Explicit “not 100% open source blanket”.

INTERFACES / CONTRACTS:
OpenAPI complete for v1.

DEPENDENCIES:
All APIs exist (after VR-087+)

INPUTS:
Code.

OUTPUTS:
Docs.

ACCEPTANCE CRITERIA:
- README run steps work on Windows PowerShell.
- LIMITATIONS.md lists no fire spread, no species, no legal-grade evidence.

TESTS:
- None.

DO NOT:
- Do not generate fake screenshots.
- Do not copy proprietary forest-dept documents.

---

## PHASE 27 — Deployment

### TODO VR-095 — Production compose, backups, healthchecks

OBJECTIVE:
Single-node deploy path for a department LAN.

FILES TO CREATE:
- `docker-compose.prod.yml`
- `docs/DEPLOYMENT.md`
- `scripts/backup_postgres.sh` and `scripts/backup_postgres.ps1`

FILES TO MODIFY:
- Dockerfiles (non-root user)
- uvicorn workers 1 for WS stickiness documented

IMPLEMENTATION:
Prod: no demo default password without override. Volume for evidence and postgres. Backup script pg_dump. Restore notes. Healthchecks on api live. Reverse proxy notes (Caddy/nginx) without requiring cloud.

INTERFACES / CONTRACTS:
LAN deployment.

DEPENDENCIES:
VR-010, VR-091, VR-092

INPUTS:
Images.

OUTPUTS:
Prod files.

ACCEPTANCE CRITERIA:
- prod compose does not ship `changeme` as only password.
- backup script documented.

TESTS:
- `docker compose -f docker-compose.prod.yml config`

DO NOT:
- Do not require AWS/GCP.
- Do not add EKS.

---

## PHASE 28 — Future Hardware Integration Preparation

### TODO VR-096 — SensorSource, DroneSource stubs, model versioning layout

OBJECTIVE:
Interfaces so FUTURE work does not rewrite the monolith — without blocking MVP.

FILES TO CREATE:
- `backend/app/sources/sensor_base.py`
- `backend/app/sources/drone_base.py`
- `backend/app/api/v1/future_ingest.py` — 501 stubs `POST /api/v1/sensors/readings` `POST /api/v1/drones/telemetry` returning 501 with message
- `models/README.md` — versioning `models/registry.json` schema `{id, version, license, sha256, task}`
- `backend/tests/unit/test_future_stubs.py`
- `docs/FUTURE.md` — IoT, drone, satellite, ReID, ML risk, fire spread, mobile app, federated learning

FILES TO MODIFY:
- ARCHITECTURE.md

IMPLEMENTATION:
Protocols:
```python
class SensorSource(Protocol):
    def read(self) -> SensorReading: ...  # temp, humidity, smoke, aq, wind
class DroneSource(Protocol):
    def frames(self) -> Iterator[Frame]: ...
    def telemetry(self) -> DroneTelemetry: ...
```
No hardware. registry.json example for onnx detector.

INTERFACES / CONTRACTS:
501 APIs clearly FUTURE. Frame still the same contract so drone can reuse detector.

DEPENDENCIES:
VR-025, VR-003

INPUTS:
None.

OUTPUTS:
Stubs + FUTURE.md.

ACCEPTANCE CRITERIA:
- Sensor/drone endpoints 501 not 200 fake data.
- registry schema documented.
- FUTURE.md does not pull those features into MVP TODOs.

TESTS:
- 501 tests.

DO NOT:
- Do not implement MAVLink.
- Do not implement LoRaWAN.
- Do not train federated models.

---

## TODO index (quick)

| ID | Name | Phase | Class |
|----|------|-------|-------|
| VR-001 | Git ignore | 0 | MVP |
| VR-002 | Language catalog | 0 | MVP |
| VR-003 | ADR | 0 | MVP |
| VR-004 | Licenses | 0 | MVP |
| VR-005 | Python skeleton | 1 | MVP |
| VR-006 | Health endpoints | 1 | MVP |
| VR-007 | Settings | 1 | MVP |
| VR-008 | Logging | 1 | MVP |
| VR-009 | Next.js skeleton | 1 | MVP |
| VR-010 | Docker Compose | 1 | MVP |
| VR-011 | Dev scripts | 1 | MVP |
| VR-012 | DB session | 2 | MVP |
| VR-013 | Alembic | 2 | MVP |
| VR-014 | Users | 2 | MVP |
| VR-015 | Geo cameras | 2 | MVP |
| VR-016 | Vision tables | 2 | MVP |
| VR-017 | Ops tables | 2 | MVP |
| VR-018 | Support tables | 2 | MVP |
| VR-019 | Demo seed | 2 | MVP |
| VR-020 | API errors | 3 | MVP |
| VR-021 | Cameras API | 3 | MVP |
| VR-022 | Zones API | 3 | MVP |
| VR-023 | Rangers API | 3 | MVP |
| VR-024 | Settings API | 3 | MVP |
| VR-025 | VideoSource | 4 | MVP |
| VR-026 | File source | 4 | MVP |
| VR-027 | Webcam | 4 | MVP |
| VR-028 | RTSP + factory | 4 | MVP |
| VR-029 | Sampler + jobs | 4 | MVP |
| VR-030 | DummyDetector | 5 | MVP |
| VR-031 | ONNX detector | 5 | MVP |
| VR-032 | Detections API | 5 | MVP |
| VR-033 | Pipeline detect | 5 | MVP |
| VR-034 | Taxonomy API | 5 | MVP |
| VR-035 | IoU tracker | 6 | MVP |
| VR-036 | ByteTrack | 6 | MVP |
| VR-037 | Tracks API | 6 | MVP |
| VR-038 | Pipeline track | 6 | MVP |
| VR-039 | ContextProvider | 7 | MVP |
| VR-040 | Georef stub | 7 | MVP |
| VR-041 | Ranger presence | 7 | MVP |
| VR-042 | Event types | 8 | MVP |
| VR-043 | EventEngine | 8 | MVP |
| VR-044 | Correlation | 8 | MVP |
| VR-045 | Events API | 8 | MVP |
| VR-046 | Risk weights | 9 | MVP |
| VR-047 | RiskEngine | 9 | MVP |
| VR-048 | Risk API | 9 | MVP |
| VR-049 | Incident SM | 10 | MVP |
| VR-050 | IncidentManager | 10 | MVP |
| VR-051 | Incidents API | 10 | MVP |
| VR-052 | History API | 10 | MVP |
| VR-053 | EvidenceStore | 11 | MVP |
| VR-054 | Capture | 11 | MVP |
| VR-055 | Evidence API | 11 | MVP |
| VR-056 | Wildlife API | 12 | MVP |
| VR-057 | Species stub | 12 | ADVANCED hook |
| VR-058 | Wildlife anomaly | 12 | MVP |
| VR-059 | Fire heuristic | 13 | MVP |
| VR-060 | Fire API | 13 | MVP |
| VR-061 | GPS ingest | 14 | MVP |
| VR-062 | SOS | 14 | MVP |
| VR-063 | Patrols + inactivity stub | 14 | MVP+FUTURE stub |
| VR-064 | Heartbeat | 15 | MVP |
| VR-065 | Empty vs stall | 15 | MVP |
| VR-066 | Tamper heuristic | 15 | MVP |
| VR-067 | WebSocket hub | 16 | MVP |
| VR-068 | Publishers | 16 | MVP |
| VR-069 | GeoJSON | 17 | MVP |
| VR-070 | Leaflet | 17 | MVP |
| VR-071 | Map layers | 17 | MVP |
| VR-072 | Command shell | 18 | MVP |
| VR-073 | API client | 18 | MVP |
| VR-074 | Overview | 18 | MVP |
| VR-075 | Incidents UI | 18 | MVP |
| VR-076 | Camera viewer | 18 | MVP |
| VR-077 | Evidence UI | 18 | MVP |
| VR-078 | Module pages | 18 | MVP |
| VR-079 | WS client | 18 | MVP |
| VR-080 | Search | 18 | MVP |
| VR-081 | Copy components | 18 | MVP |
| VR-082 | Analytics UI | 18 | MVP |
| VR-083 | JWT | 19 | MVP |
| VR-084 | RBAC | 19 | MVP |
| VR-085 | Login UI | 19 | MVP |
| VR-086 | Edge outbox | 20 | MVP |
| VR-087 | Sync API | 20 | MVP |
| VR-088 | Offline demo | 20 | MVP |
| VR-089 | Outcomes | 21 | MVP |
| VR-090 | E2E seven demos | 22 | MVP |
| VR-091 | Security | 23 | MVP |
| VR-092 | Perf/metrics | 24 | MVP |
| VR-093 | Demo runbook | 25 | MVP |
| VR-094 | Docs | 26 | MVP |
| VR-095 | Prod compose | 27 | PRODUCTION ARCH |
| VR-096 | Future stubs | 28 | FUTURE prep |

---

*OpenCode: implement VR-001 next. Stop after its ACCEPTANCE CRITERIA.*
