# VANRAKSHA AI — Complete Engineering Master Plan

**Audit 2026-09-02:** `C:\Users\shaur\OneDrive\Desktop\SIH` is empty (0 files, no git). OpenCode creates the tree from chat TODOs VR-001–VR-202. This document is the scope map, not a substitute for those contracts.

---

## Existing Source Files
0

## Atomic TODOs (VR-001–202)
202

## Runtime Processes
4 (db, api, web, optional edge sim)

## License Obligation
**AGPL** — Ultralytics (YOLO/ByteTrack) is AGPL-3.0. The app must be open-sourced or use Enterprise license (not used). Detector protocol allows swap to YOLOX (Apache-2.0) if AGPL is blocked.

---

## Core Differentiation
**Correlation + Explainable Risk + Incidents** — not a second YOLO demo.  
MVP must ship **DETECT → UNDERSTAND → CORRELATE → ASSESS → RESPOND** on file video without hardware.  
**Never emit "Poacher detected."**

---

## Intelligence Pipeline (All Scopes)

```
Source → Detect → Track → Context → Correlate → Risk → Incident → Command
```

Each box is a Python protocol in `vision/` or `backend/services/`.

---

## Architecture

| Layer | Technology |
|-------|------------|
| **App** | Modular monolith — one FastAPI app: HTTP, WebSocket, in-process jobs |
| **Vision** | `vanraksha_vision` package — zero FastAPI imports |
| **DB** | PostGIS for zones/cameras/rangers |
| **Frontend** | Next.js command centre |
| **Infra** | Docker Compose only — no Kubernetes |
| **Offline MVP** | SQLite outbox + `POST /api/v1/sync/ingest`, simulated as a second process |

---

## Language & Evidence

| Concept | Rule |
|---------|------|
| **Detection classes** | person / vehicle / wildlife / smoke / fire (if model present) |
| **Event types** | suspicious_activity, wildlife_observation, possible_fire_smoke, camera_health |
| **Incident copy** | "High-risk suspicious activity. Ranger verification required." |
| **Evidence** | Timestamped investigation support — **not** "legally admissible" |
| **Integrity** | SHA-256 on files |

---

## Feature Scope

| Capability | Horizon | Note |
|------------|---------|------|
| Video file + YOLO + ByteTrack IDs | **MVP** | Core differentiator starts after this |
| Rule events + correlation + explainable risk | **MVP** | Product vs camera-alert tools |
| Incidents, evidence JPEGs+hash, command map | **MVP** | Forest-officer demo |
| Auth JWT four roles, audit log | **MVP** | Required before any shared deploy |
| Simulated ranger GPS + SOS | **MVP** | No mobile app yet |
| Simulated edge outbox + sync | **MVP** | No physical edge box |
| Species classification / MegaDetector | **ADVANCED** | Protocol in MVP, model later |
| Fire-spread / wind physics | **FUTURE** | MVP: detect + zone only |
| Cross-camera ReID | **FUTURE** | track_id is per camera/job |
| ML risk model | **FUTURE** | Keep rule engine |
| IoT / drone / satellite / wearables | **FUTURE** | Source protocols only |
| K8s, Kafka, Redis, paid SMS | **FUTURE** | Not in architecture |

---

## Phase Index (OpenCode IDs)

| Phase | Name | TODO IDs | Horizon |
|-------|------|----------|---------|
| 0 | Audit & contracts | VR-001–002 | MVP |
| 1 | Foundation | VR-003–016 | MVP |
| 2 | Database | VR-017–028 | MVP |
| 3 | Backend core | VR-029–034 | MVP |
| 4 | Video ingestion | VR-035–042 | MVP |
| 5 | Detection | VR-043–049 | MVP |
| 6 | Tracking | VR-050–055 | MVP |
| 7 | Geospatial context | VR-056–061 | MVP |
| 8 | Event + correlation | VR-062–070 | MVP |
| 9 | Risk engine | VR-071–075 | MVP |
| 10 | Incidents | VR-076–082 | MVP |
| 11 | Evidence | VR-083–087 | MVP |
| 12 | Wildlife intel | VR-088–093 | MVP+Adv |
| 13 | Fire intel | VR-094–098 | MVP+Fut |
| 14 | Ranger safety | VR-099–106 | MVP+Adv |
| 15 | Camera health | VR-107–111 | MVP |
| 16 | WebSockets | VR-112–115 | MVP |
| 17 | GIS APIs | VR-116–119 | MVP |
| 18 | Command centre UI | VR-120–138 | MVP+Adv |
| 19 | AuthZ / RBAC | VR-139–146 | MVP |
| 20 | Offline sync | VR-147–154 | MVP sim |
| 21 | Analytics | VR-155–159 | Adv |
| 22 | Testing | VR-160–168 | MVP |
| 23 | Security | VR-169–174 | MVP |
| 24 | Performance | VR-175–178 | MVP+Adv |
| 25 | SIH demos | VR-179–186 | MVP |
| 26 | Documentation | VR-187–191 | MVP |
| 27 | Deployment | VR-192–195 | Adv |
| 28 | Hardware adapters | VR-196–202 | Future |

---

## Parallel Tracks After VR-016

- **Database** (VR-017+) and **Next.js shell** (VR-014/120) can proceed together
- **Vision** (VR-035+) does not wait on incident tables
- **Auth** (VR-139) should land before demo-to-judges on a shared network; local stub job can run without auth until VR-139, then lock APIs

---

## Definition of Done

### A. MVP Complete
- File video through YOLO+track IDs
- Correlated suspicious incident with factor list
- Evidence JPEG+hash
- Leaflet command centre
- JWT roles
- Simulated ranger SOS
- Simulated offline sync
- pytest e2e on stub tracker

### B. SIH Demo Ready
- Seven scripted demos (suspicious, wildlife, fire stub, camera fail, SOS, correlation, offline sync)
- DEMO.md with timings
- User-supplied wildlife/person MP4 for real boxes

### C. Production Architecture
- Secrets, RBAC, audit, rate limits, indexes, health/ready, retention config, license review recorded
- **Not** the same as a live forest deployment