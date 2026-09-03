"""Add tracks_count, events_count, incidents_count to ingest_jobs.

Revision ID: 0002_add_job_progress_fields
Revises: 0001_initial
Create Date: 2026-09-03
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_job_progress_fields"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ingest_jobs", sa.Column("tracks_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ingest_jobs", sa.Column("events_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("ingest_jobs", sa.Column("incidents_count", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("ingest_jobs", "incidents_count")
    op.drop_column("ingest_jobs", "events_count")
    op.drop_column("ingest_jobs", "tracks_count")