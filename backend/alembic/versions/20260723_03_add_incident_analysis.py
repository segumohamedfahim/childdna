"""Add incident_analyses table for AI intelligence engine

Revision ID: 20260723_03_add_incident_analysis
Revises: 20260723_02_add_rescue_tables
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "20260723_03_add_incident_analysis"
down_revision = "20260723_02_add_rescue_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create incident_analyses table."""
    op.create_table(
        "incident_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "incident_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column(
            "analysis_engine",
            sa.String(50),
            nullable=False,
            server_default="rule_engine_v1",
        ),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("gender_confidence", sa.Float(), nullable=True),
        sa.Column("estimated_age_min", sa.Integer(), nullable=True),
        sa.Column("estimated_age_max", sa.Integer(), nullable=True),
        sa.Column("age_confidence", sa.Float(), nullable=True),
        sa.Column("emotion", sa.String(50), nullable=True),
        sa.Column("emotion_confidence", sa.Float(), nullable=True),
        sa.Column("clothing", sa.JSON(), nullable=True),
        sa.Column("clothing_confidence", sa.Float(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("location_confidence", sa.Float(), nullable=True),
        sa.Column("distinguishing_features", sa.JSON(), nullable=True),
        sa.Column("features_confidence", sa.Float(), nullable=True),
        sa.Column(
            "overall_confidence",
            sa.Float(),
            nullable=False,
            server_default="0.0",
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
            ["incident_id"], ["rescue_sessions.id"]
        ),
    )
    op.create_index(
        "ix_incident_analyses_incident_id",
        "incident_analyses",
        ["incident_id"],
        unique=True,
    )
    op.create_index(
        "ix_incident_analyses_confidence",
        "incident_analyses",
        ["overall_confidence"],
    )


def downgrade() -> None:
    """Drop incident_analyses table."""
    op.drop_index(
        "ix_incident_analyses_confidence",
        table_name="incident_analyses",
    )
    op.drop_index(
        "ix_incident_analyses_incident_id",
        table_name="incident_analyses",
    )
    op.drop_table("incident_analyses")