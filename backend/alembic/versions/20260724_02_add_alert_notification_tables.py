"""Add alerts and notifications tables for Alert & Notification system

Revision ID: 20260724_02_add_alert_notification_tables
Revises: 20260724_01_add_incident_matches
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260724_02_add_alert_notification_tables"
down_revision = "20260724_01_add_incident_matches"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create alerts and notifications tables."""
    # Create alerts table
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "matched_incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "alert_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(20),
            nullable=False,
            server_default="low",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(1000),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(50),
            nullable=False,
            server_default="system",
        ),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column(
            "acknowledged_by",
            sa.String(255),
            nullable=True,
        ),
        sa.Column(
            "acknowledged_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "resolved_by",
            sa.String(255),
            nullable=True,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"], ["rescue_sessions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["matched_incident_id"], ["rescue_sessions.id"],
        ),
    )
    op.create_index(
        "ix_alerts_incident_id", "alerts", ["incident_id"],
    )
    op.create_index(
        "ix_alerts_status", "alerts", ["status"],
    )
    op.create_index(
        "ix_alerts_severity", "alerts", ["severity"],
    )
    op.create_index(
        "ix_alerts_created_at", "alerts", ["created_at"],
    )

    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "guardian_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "child_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "notification_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "channel",
            sa.String(20),
            nullable=False,
            server_default="in_app",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "message",
            sa.String(2000),
            nullable=False,
        ),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "delivered_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["guardian_id"], ["guardians.id"],
        ),
        sa.ForeignKeyConstraint(
            ["child_id"], ["children.id"],
        ),
        sa.ForeignKeyConstraint(
            ["incident_id"], ["rescue_sessions.id"],
        ),
    )
    op.create_index(
        "ix_notifications_guardian_id", "notifications", ["guardian_id"],
    )
    op.create_index(
        "ix_notifications_status", "notifications", ["status"],
    )
    op.create_index(
        "ix_notifications_created_at", "notifications", ["created_at"],
    )


def downgrade() -> None:
    """Drop alerts and notifications tables."""
    op.drop_index(
        "ix_notifications_created_at", table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_status", table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_guardian_id", table_name="notifications",
    )
    op.drop_table("notifications")
    op.drop_index(
        "ix_alerts_created_at", table_name="alerts",
    )
    op.drop_index(
        "ix_alerts_severity", table_name="alerts",
    )
    op.drop_index(
        "ix_alerts_status", table_name="alerts",
    )
    op.drop_index(
        "ix_alerts_incident_id", table_name="alerts",
    )
    op.drop_table("alerts")