"""Add incident_matches table for REUNITE Match engine

Revision ID: 20260724_01_add_incident_matches
Revises: 20260723_03_add_incident_analysis
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260724_01_add_incident_matches"
down_revision = "20260723_03_add_incident_analysis"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create incident_matches table."""
    op.create_table(
        "incident_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "matched_incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "similarity_score",
            sa.Float(),
            nullable=False,
            server_default="0.0",
        ),
        sa.Column(
            "match_category",
            sa.String(20),
            nullable=False,
            server_default="no_match",
        ),
        sa.Column(
            "recommendation",
            sa.String(20),
            nullable=False,
            server_default="no_action",
        ),
        sa.Column(
            "algorithm_version",
            sa.String(50),
            nullable=False,
            server_default="rule_engine_v1",
        ),
        sa.Column("score_breakdown", sa.JSON(), nullable=True),
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
            ["incident_id"], ["rescue_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["matched_incident_id"], ["rescue_sessions.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_incident_matches_incident_id",
        "incident_matches",
        ["incident_id"],
    )
    op.create_index(
        "ix_incident_matches_incident_score",
        "incident_matches",
        ["incident_id", "similarity_score"],
    )
    op.create_index(
        "ix_incident_matches_matched_incident_id",
        "incident_matches",
        ["matched_incident_id"],
    )


def downgrade() -> None:
    """Drop incident_matches table."""
    op.drop_index(
        "ix_incident_matches_matched_incident_id",
        table_name="incident_matches",
    )
    op.drop_index(
        "ix_incident_matches_incident_score",
        table_name="incident_matches",
    )
    op.drop_index(
        "ix_incident_matches_incident_id",
        table_name="incident_matches",
    )
    op.drop_table("incident_matches")
