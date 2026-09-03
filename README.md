# VANRAKSHA AI — Forest Command Centre

Detection, correlation, explainable risk, and incident management for forest operations.

> **Never emits "poacher detected."** All AI outputs require human verification.

## Stack

- **Backend**: FastAPI, SQLAlchemy 2.x, PostgreSQL 16 + PostGIS 3, ONNX Runtime + YOLOX, ByteTrack
- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind, Leaflet
- **Infra**: Docker Compose (single-node)

## Quick Start (Linux/macOS)

```bash
# 1. Install deps
pip install -e .
cd frontend && npm install && cd ..

# 2. Configure environment
cp .env.example .env
# edit .env as needed

# 3. Start stack
docker compose up --build

# 4. Run migrations (separate terminal)
docker compose run --rm api alembic -c backend/alembic.ini upgrade head

# 5. Seed demo data
docker compose run --rm api python scripts/seed_demo.py
```

- API: http://localhost:8000
- OpenAPI: http://localhost:8000/openapi.json
- Frontend: http://localhost:3000
- Health: http://localhost:8000/api/v1/health/live

## Quick Start (Windows PowerShell)

```powershell
# 1. Install deps
pip install -e .
cd frontend; npm install; cd ..

# 2. Configure environment
Copy-Item .env.example .env
# edit .env

# 3. Start stack
docker compose up --build

# 4. Run migrations (separate terminal)
docker compose run --rm api alembic -c backend/alembic.ini upgrade head

# 5. Seed demo data
docker compose run --rm api python scripts/seed_demo.py
```

## Development

```bash
# Backend tests
docker compose run --rm api python -m pytest backend/tests -q

# Frontend typecheck
cd frontend && npm run typecheck

# Lint
docker compose run --rm api python -m ruff check backend/app
```

Or use the Makefile / PowerShell helper:
```bash
make dev      # start all services
make test     # run tests
make migrate  # run migrations
make lint     # run linter
```

```powershell
.\scripts\dev.ps1 -Command dev
.\scripts\dev.ps1 -Command test
```

## Model Weights

Default detector is a deterministic `DummyDetector` (no weights needed). To enable ONNX YOLOX:

```bash
python scripts/download_models.py
# Place .onnx files in ./models/
# Set DETECTOR_BACKEND=onnx in .env
```

## License Policy

Default is **AGPL-blocked**. Ultralytics/BoxMOT are forbidden unless `ALLOW_AGPL=true` is set with explicit approval. See `config/license_policy.yaml` and `docs/THIRD_PARTY_LICENSES.md`.

## Architecture

See `docs/ARCHITECTURE.md` for the ADR and `docs/LANGUAGE.md` for terminology rules.