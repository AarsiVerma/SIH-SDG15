#!/bin/bash
# PostgreSQL restore script for VANRAKSHA AI

set -e

BACKUP_FILE="${1:-}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_NAME="${POSTGRES_DB:-vanraksha}"
DB_USER="${POSTGRES_USER:-vanraksha}"
CONTAINER="${CONTAINER:-vanraksha-db-prod}"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.sql.gz>"
  echo "Available backups:"
  ls -lh "$BACKUP_DIR"/vanraksha_*.sql.gz 2>/dev/null || echo "No backups found"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "[$(date)] Restoring $DB_NAME from $BACKUP_FILE..."
echo "WARNING: This will OVERWRITE the current database!"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Terminate existing connections
docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"

# Drop and recreate database
docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
docker exec "$CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"

# Restore
gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"

echo "[$(date)] Restore complete."

# Run migrations to ensure schema is current
echo "Running migrations..."
docker compose -f docker-compose.prod.yml run --rm api alembic -c backend/alembic.ini upgrade head

echo "[$(date)] Done."