# Third-Party License Registry — VANRAKSHA AI

Living document. Every runtime and dev dependency is listed with its license
and a status. The project does **not** claim to be "100% open source" as a
blanket statement; licenses are checked per component and some items marked
"requires additional review".

Status values: `planned` (not yet added to `pyproject.toml`/`package.json`),
`added`, `blocked`, `requires_review`.

| Component | License | Status | Notes |
|-----------|---------|--------|-------|
| FastAPI | MIT | planned | — |
| Uvicorn | BSD-3 | planned | — |
| Pydantic / pydantic-settings | MIT | planned | — |
| SQLAlchemy 2.x | MIT | planned | — |
| Alembic | MIT | planned | — |
| psycopg 3 | LGPL-3 | planned | — |
| GeoAlchemy2 | MIT | planned | — |
| numpy | BSD-3 | planned | — |
| opencv-python-headless | Apache-2.0 | planned | — |
| onnxruntime | MIT | planned | — |
| PyYAML | MIT | planned | — |
| httpx | BSD-3 | planned | — |
| pytest / pytest-asyncio | MIT | planned | — |
| PostGIS | GPL-2 | planned | **GPL** — legal review required before distribution |
| Next.js | MIT | planned | — |
| React | MIT | planned | — |
| Tailwind CSS | MIT | planned | — |
| Leaflet | BSD-2-Clause | planned | Use vanilla Leaflet |
| react-leaflet | Hippocratic? | **requires_review** | Re-verify; if Hippocratic use vanilla Leaflet + useRef |
| YOLOX (ONNX) | Apache-2.0 | planned | Default detector |
| ByteTrack | MIT | planned | Vendor minimal port, keep LICENSE header |
| Ultralytics (YOLO/ByteTrack) | AGPL-3.0 | **blocked** | `allow_agpl: false`; do not add |
| BoxMOT | AGPL-3.0 | **blocked** | `forbidden_packages` |
| MegaDetector | MIT (weights license differs) | requires_review | Optional, ADVANCED only |
| FFmpeg | LGPL/GPL variant | requires_review | Only for decode/encode; document build flags |

## Decision log

- **YOLOX vs Ultralytics**: YOLOX chosen because Ultralytics is AGPL-3.0 and the
  project defaults to `allow_agpl: false`. If an AGPL flag is ever flipped, the
  whole project must be open-sourced under AGPL-compatible terms — this requires
  explicit human approval, not an env var flip alone.
- **react-leaflet**: license must be re-verified before use; default plan is
  vanilla Leaflet wrapped with `useEffect`.
- This registry is enforced in CI (VR-091): `config/license_policy.yaml`
  forbidden packages must not appear in lockfiles.