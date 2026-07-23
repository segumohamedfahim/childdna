"""Add rescue_sessions, timeline_events, reunion_records tables

Revision ID: 20260723_02_add_rescue_tables
Revises: 20260723_01_initial
Create Date: 2026-07-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "20260723_02_add_rescue_tables"
down_revision = "20260723_01_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create rescue_sessions, timeline_events, reunion_records tables."""
    op.create_table(
        "rescue_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("rescuer_name", sa.String(255), nullable=True),
        sa.Column("rescuer_phone", sa.String(20), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("location_name", sa.String(255), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
    )
    op.create_index(
        "ix_rescue_sessions_child_id", "rescue_sessions", ["child_id"]
    )
    op.create_index(
        "ix_rescue_sessions_status", "rescue_sessions", ["status"]
    )

    op.create_table(
        "timeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "rescue_session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("location_name", sa.String(255), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
        sa.ForeignKeyConstraint(
            ["rescue_session_id"], ["rescue_sessions.id"]
        ),
    )
    op.create_index(
        "ix_timeline_events_child_id", "timeline_events", ["child_id"]
    )
    op.create_index(
        "ix_timeline_events_session_id",
        "timeline_events",
        ["rescue_session_id"],
    )
    op.create_index(
        "ix_timeline_events_event_type", "timeline_events", ["event_type"]
    )

    op.create_table(
        "reunion_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rescuer_name", sa.String(255), nullable=False),
        sa.Column("guardian_name", sa.String(255), nullable=False),
        sa.Column("reunion_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verification_method", sa.String(100), nullable=False),
        sa.Column("remarks", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
    )
    op.create_index(
        "ix_reunion_records_child_id", "reunion_records", ["child_id"]
    )


def downgrade() -> None:
    """Drop rescue_sessions, timeline_events, reunion_records tables."""
    op.drop_index("ix_reunion_records_child_id", table_name="reunion_records")
    op.drop_table("reunion_records")
    op.drop_index(
        "ix_timeline_events_event_type", table_name="timeline_events"
    )
    op.drop_index(
        "ix_timeline_events_session_id", table_name="timeline_events"
    )
    op.drop_index(
        "ix_timeline_events_child_id", table_name="timeline_events"
    )
    op.drop_table("timeline_events")
    op.drop_index(
        "ix_rescue_sessions_status", table_name="rescue_sessions"
    )
    op.drop_index(
        "ix_rescue_sessions_child_id", table_name="rescue_sessions"
    )
    op.drop_table("rescue_sessions")