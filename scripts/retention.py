"""Data retention management script.

This script implements the retention policy for high-volume tables.
Run periodically (e.g., daily via cron) to clean up old data.

Tables covered:
- detections: DETECTION_RETENTION_DAYS (default 30)
- track_points: TRACK_POINTS_RETENTION_DAYS (default 30)
- events: EVENT_RETENTION_DAYS (default 90)
- camera_health: CAMERA_HEALTH_RETENTION_DAYS (default 30)
- ranger_locations: RANGER_LOCATION_RETENTION_DAYS (default 30)
- audit_logs: AUDIT_LOG_RETENTION_DAYS (default 365)
- notifications: NOTIFICATION_RETENTION_DAYS (default 90)
- sync_outbox: SYNC_OUTBOX_RETENTION_DAYS (default 30)

Evidence and incidents are NOT auto-deleted - they require manual review.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session, engine
from app.models import (
    Detection, TrackPoint, Event, CameraHealth, RangerLocation,
    AuditLog, Notification, SyncOutbox, Evidence, Incident
)
from app.core.config import get_settings

logger = logging.getLogger("app.retention")
settings = get_settings()


# Retention periods (days)
RETENTION_CONFIG = {
    "detections": getattr(settings, "detection_retention_days", 30),
    "track_points": getattr(settings, "track_points_retention_days", 30),
    "events": getattr(settings, "event_retention_days", 90),
    "camera_health": getattr(settings, "camera_health_retention_days", 30),
    "ranger_locations": getattr(settings, "ranger_location_retention_days", 30),
    "audit_logs": getattr(settings, "audit_log_retention_days", 365),
    "notifications": getattr(settings, "notification_retention_days", 90),
    "sync_outbox": getattr(settings, "sync_outbox_retention_days", 30),
}

# Tables that should NOT be auto-deleted
PROTECTED_TABLES = {
    "evidence",      # Legal evidence
    "incidents",     # Incident records
    "incident_events", "incident_status_history", "incident_outcomes",
    "tracks",        # Track metadata (lightweight)
    "cameras", "zones", "forests", "rangers", "users",
    "camera_sources", "ingest_jobs", "patrols", "wildlife_observations",
}


async def get_retention_days(table_name: str) -> int:
    """Get retention period for a table from config."""
    return RETENTION_CONFIG.get(table_name, 30)


async def cleanup_table(
    session: AsyncSession,
    model,
    date_column: str,
    table_name: str,
    dry_run: bool = False,
) -> int:
    """Delete rows older than retention period."""
    retention_days = await get_retention_days(table_name)
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    
    stmt = delete(model).where(getattr(model, date_column) < cutoff)
    
    if dry_run:
        # Count rows that would be deleted
        count_stmt = select(func.count()).select_from(
            stmt.compile(compile_kwargs={"literal_binds": True}).statement
        )
        # Simple count for dry run
        count = await session.scalar(
            select(func.count()).where(getattr(model, date_column) < cutoff).select_from(model.__table__)
        )
        logger.info("[DRY RUN] Would delete %d rows from %s older than %s", count, table_name, cutoff)
        return count
    
    result = await session.execute(stmt)
    deleted = result.rowcount
    logger.info("Deleted %d rows from %s older than %s", deleted, table_name, cutoff)
    return deleted


async def cleanup_detections(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old detections."""
    return await cleanup_table(
        session, Detection, "captured_at", "detections", dry_run
    )


async def cleanup_track_points(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old track points."""
    return await cleanup_table(
        session, TrackPoint, "captured_at", "track_points", dry_run
    )


async def cleanup_events(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old events."""
    return await cleanup_table(
        session, Event, "created_at", "events", dry_run
    )


async def cleanup_camera_health(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old camera health records (keep latest per camera)."""
    retention_days = await get_retention_days("camera_health")
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    
    # Keep only the latest health record per camera
    # Delete older records beyond the latest
    from sqlalchemy import text
    
    if dry_run:
        count_stmt = text("""
            SELECT COUNT(*) FROM camera_health 
            WHERE last_heartbeat < :cutoff
            AND id NOT IN (
                SELECT DISTINCT ON (camera_id) id 
                FROM camera_health 
                ORDER BY camera_id, last_heartbeat DESC
            )
        """)
        count = await session.scalar(count_stmt, {"cutoff": cutoff})
        logger.info("[DRY RUN] Would delete %d camera health rows", count)
        return count
    
    stmt = text("""
        DELETE FROM camera_health 
        WHERE last_heartbeat < :cutoff
        AND id NOT IN (
            SELECT DISTINCT ON (camera_id) id 
            FROM camera_health 
            ORDER BY camera_id, last_heartbeat DESC
        )
    """)
    result = await session.execute(stmt, {"cutoff": cutoff})
    logger.info("Deleted %d camera health rows", result.rowcount)
    return result.rowcount


async def cleanup_ranger_locations(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old ranger locations."""
    return await cleanup_table(
        session, RangerLocation, "captured_at", "ranger_locations", dry_run
    )


async def cleanup_audit_logs(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old audit logs."""
    return await cleanup_table(
        session, AuditLog, "at", "audit_logs", dry_run
    )


async def cleanup_notifications(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up old notifications."""
    return await cleanup_table(
        session, Notification, "created_at", "notifications", dry_run
    )


async def cleanup_sync_outbox(session: AsyncSession, dry_run: bool = False) -> int:
    """Clean up synced outbox entries."""
    retention_days = await get_retention_days("sync_outbox")
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    
    if dry_run:
        count = await session.scalar(
            select(func.count()).where(
                SyncOutbox.synced_at.isnot(None),
                SyncOutbox.synced_at < cutoff
            )
        )
        logger.info("[DRY RUN] Would delete %d synced outbox rows", count)
        return count
    
    stmt = delete(SyncOutbox).where(
        SyncOutbox.synced_at.isnot(None),
        SyncOutbox.synced_at < cutoff
    )
    result = await session.execute(stmt)
    logger.info("Deleted %d synced outbox rows", result.rowcount)
    return result.rowcount


async def run_retention(dry_run: bool = False) -> dict:
    """Run all retention cleanup tasks."""
    logger.info("Starting retention cleanup (dry_run=%s)", dry_run)
    results = {}
    
    async for session in get_session():
        try:
            results["detections"] = await cleanup_detections(session, dry_run)
            results["track_points"] = await cleanup_track_points(session, dry_run)
            results["events"] = await cleanup_events(session, dry_run)
            results["camera_health"] = await cleanup_camera_health(session, dry_run)
            results["ranger_locations"] = await cleanup_ranger_locations(session, dry_run)
            results["audit_logs"] = await cleanup_audit_logs(session, dry_run)
            results["notifications"] = await cleanup_notifications(session, dry_run)
            results["sync_outbox"] = await cleanup_sync_outbox(session, dry_run)
            
            if not dry_run:
                await session.commit()
            
        except Exception as e:
            logger.exception("Retention cleanup failed: %s", e)
            await session.rollback()
            raise
    
    total = sum(results.values())
    logger.info("Retention cleanup complete. Total rows deleted: %d", total)
    return results


async def main():
    """Main entry point for CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data retention cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        results = await run_retention(dry_run=args.dry_run)
        print("Retention cleanup results:")
        for table, count in results.items():
            print(f"  {table}: {count} rows")
        print(f"Total: {sum(results.values())} rows")
    except Exception as e:
        logger.exception("Retention cleanup failed: %s", e)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))