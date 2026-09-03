#!/bin/bash
# PostgreSQL backup script for VANRAKSHA AI
# Runs inside db container or from host

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_NAME="${POSTGRES_DB:-vanraksha}"
DB_USER="${POSTGRES_USER:-vanraksha}"
CONTAINER="${CONTAINER:-vanraksha-db-prod}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup of $DB_NAME..."

# Dump from container
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-privileges | \
  gzip > "$BACKUP_DIR/vanraksha_${DATE}.sql.gz"

# Verify backup
if [ -f "$BACKUP_DIR/vanraksha_${DATE}.sql.gz" ] && [ -s "$BACKUP_DIR/vanraksha_${DATE}.sql.gz" ]; then
  echo "[$(date)] Backup complete: $BACKUP_DIR/vanraksha_${DATE}.sql.gz"
  ls -lh "$BACKUP_DIR/vanraksha_${DATE}.sql.gz"
else
  echo "[$(date)] ERROR: Backup file missing or empty!"
  exit 1
fi

# Retention: keep last 30 days
echo "[$(date)] Cleaning old backups (>30 days)..."
find "$BACKUP_DIR" -name "vanraksha_*.sql.gz" -mtime +30 -delete

echo "[$(date)] Done."