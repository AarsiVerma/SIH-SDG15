# VANRAKSHA AI — Production Deployment Guide

## Overview

Single-node Docker Compose deployment for department LAN. No cloud, no Kubernetes.

## Requirements

- Linux server (Ubuntu 22.04+ recommended)
- Docker 24+ and Docker Compose v2
- 8 GB RAM minimum (16 GB recommended)
- 100 GB disk (50 GB for DB + evidence + models)
- NVIDIA GPU optional (for ONNX CUDA provider)

## Quick Deploy

```bash
# 1. Clone / copy project
git clone <repo> vanraksha-ai
cd vanraksha-ai

# 2. Configure environment
cp .env.example .env
# Edit .env — CRITICAL: change SECRET_KEY, DATABASE_URL if remote DB

# 3. Build and start
docker compose -f docker-compose.prod.yml up -d --build

# 4. Run migrations
docker compose -f docker-compose.prod.yml run --rm api \
  alembic -c backend/alembic.ini upgrade head

# 5. Seed demo data (optional)
docker compose -f docker-compose.prod.yml run --rm api python scripts/seed_demo.py
```

## Production Compose (`docker-compose.prod.yml`)

Key differences from dev:
- No bind mounts (images baked)
- Non-root user in containers
- Uvicorn workers=1 (WebSocket sticky)
- Resource limits
- No `DEBUG=true`

```yaml
version: "3.9"
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: vanraksha
      POSTGRES_USER: vanraksha
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vanraksha -d vanraksha"]
      interval: 10s
    networks: [vanraksha-net]

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    image: vanraksha/api:prod
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
    environment:
      - DATABASE_URL=postgresql+psycopg://vanraksha:vanraksha@db:5432/vanraksha
      - PYTHONPATH=/app
    volumes:
      - evidence:/app/evidence
      - models:/app/models
    depends_on:
      db:
        condition: service_healthy
    networks: [vanraksha-net]
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    image: vanraksha/web:prod
    command: npm run start
    environment:
      - NEXT_PUBLIC_API_URL=https://your-domain/api/v1
    depends_on: [api]
    networks: [vanraksha-net]

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    image: vanraksha/api:prod
    command: python -m app.worker
    environment:
      - DATABASE_URL=postgresql+psycopg://vanraksha:vanraksha@db:5432/vanraksha
    volumes:
      - evidence:/app/evidence
      - models:/app/models
    depends_on:
      db:
        condition: service_healthy
    networks: [vanraksha-net]
    deploy:
      resources:
        limits:
          memory: 2G

volumes:
  pgdata:
  evidence:
  models:

secrets:
  db_password:
    file: ./secrets/db_password.txt

networks:
  vanraksha-net:
    driver: bridge
```

## Reverse Proxy (Caddy — Recommended)

```caddy
your-domain.com {
    reverse_proxy web:3000
}

api.your-domain.com {
    reverse_proxy api:8000
}
```

- Automatic HTTPS via Let's Encrypt
- WebSocket support built-in
- Replace with Nginx if preferred

## Environment Variables (Production)

| Variable | Required | Example |
|----------|----------|---------|
| `SECRET_KEY` | **YES** | `openssl rand -base64 32` |
| `DATABASE_URL` | **YES** | `postgresql+psycopg://...` |
| `ENVIRONMENT` | **YES** | `production` |
| `DEBUG` | No | `false` |
| `ALLOW_AGPL` | No | `false` |
| `DEMO_MODE` | No | `false` |
| `CORS_ORIGINS` | **YES** | `["https://your-domain.com"]` |
| `EVIDENCE_DIR` | No | `/app/evidence` |
| `MODELS_DIR` | No | `/app/models` |

## Secrets Management

- `SECRET_KEY` and `DB_PASSWORD` via Docker secrets (files in `./secrets/`)
- Never commit `.env` or secrets to git

## Backup & Restore

```bash
# Backup (run on host)
./scripts/backup_postgres.sh

# Restore
./scripts/restore_postgres.sh backup_20260902.sql.gz

# Evidence backup
tar -czf evidence_backup.tar.gz /var/lib/docker/volumes/vanraksha_evidence/_data
```

### backup_postgres.sh

```bash
#!/bin/bash
set -e
DATE=$(date +%Y%m%d_%H%M%S)
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U vanraksha vanraksha | gzip > "backups/vanraksha_${DATE}.sql.gz"
# Keep last 30 days
find backups -name "vanraksha_*.sql.gz" -mtime +30 -delete
```

## Monitoring

- Health: `GET /api/v1/health/ready`
- Metrics: `GET /api/v1/metrics` (admin only, Prometheus text)
- Logs: `docker compose -f docker-compose.prod.yml logs -f api`

## Upgrades

```bash
# 1. Pull new images
docker compose -f docker-compose.prod.yml pull

# 2. Run migrations
docker compose -f docker-compose.prod.yml run --rm api \
  alembic -c backend/alembic.ini upgrade head

# 3. Restart services
docker compose -f docker-compose.prod.yml up -d --no-deps api web worker
```

## Rollback

```bash
# Restore DB from backup
gunzip -c backups/vanraksha_20260902_120000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U vanraksha vanraksha

# Deploy previous image tag
docker compose -f docker-compose.prod.yml up -d --no-deps api web worker
```

## Security Checklist

- [ ] `SECRET_KEY` rotated from default
- [ ] `DEBUG=false`
- [ ] `DEMO_MODE=false`
- [ ] `ALLOW_AGPL=false`
- [ ] `CORS_ORIGINS` locked to domain
- [ ] HTTPS via Caddy/Nginx
- [ ] DB password in Docker secret
- [ ] Non-root containers
- [ ] Resource limits set
- [ ] Backup script cron'd daily
- [ ] Log rotation configured

## Hardware Recommendations

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk | 100 GB SSD | 500 GB NVMe |
| GPU | None | NVIDIA T4 / RTX 3080+ (for CUDA ONNX) |

## Network

- Expose only 80/443 via reverse proxy
- Database not exposed externally
- Worker has no inbound ports
- LAN-only deployment assumed