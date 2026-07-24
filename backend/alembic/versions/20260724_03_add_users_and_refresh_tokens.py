"""Add users and refresh_tokens tables for Authentication & Authorization

Revision ID: 20260724_03_add_users_and_refresh_tokens
Revises: 20260724_02_add_alert_notification_tables
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260724_03_add_users_and_refresh_tokens"
down_revision = "20260724_02_add_alert_notification_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users and refresh_tokens tables."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(20),
            nullable=True,
        ),
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default="guardian",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "guardian_id",
            postgresql.UUID(as_uuid=True),
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
            ["guardian_id"], ["guardians.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_users_email", "users", ["email"], unique=True,
    )
    op.create_index(
        "ix_users_role", "users", ["role"],
    )
    op.create_index(
        "ix_users_guardian_id", "users", ["guardian_id"],
    )

    # Create refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "token_hash",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "device_info",
            sa.String(500),
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
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"],
    )
    op.create_index(
        "ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"],
    )
    op.create_index(
        "ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"],
    )


def downgrade() -> None:
    """Drop refresh_tokens and users tables."""
    op.drop_index(
        "ix_refresh_tokens_expires_at", table_name="refresh_tokens",
    )
    op.drop_index(
        "ix_refresh_tokens_token_hash", table_name="refresh_tokens",
    )
    op.drop_index(
        "ix_refresh_tokens_user_id", table_name="refresh_tokens",
    )
    op.drop_table("refresh_tokens")
    op.drop_index(
        "ix_users_guardian_id", table_name="users",
    )
    op.drop_index(
        "ix_users_role", table_name="users",
    )
    op.drop_index(
        "ix_users_email", table_name="users",
    )
    op.drop_table("users")