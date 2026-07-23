"""Initial migration - Core domain models with revoked_at field"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "20260723_01_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables"""
    op.create_table(
        "children",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("guardian_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("nickname", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("blood_group", sa.String(10), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("special_needs", sa.Text(), nullable=True),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(50), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    
    op.create_table(
        "child_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_code", sa.String(100), nullable=False),
        sa.Column("qr_secret", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"]),
    )
    
    op.create_index("ix_child_tokens_token_code", "child_tokens", ["token_code"])
    op.create_index("ix_child_tokens_child_id", "child_tokens", ["child_id"])


def downgrade() -> None:
    """Drop tables"""
    op.drop_index("ix_child_tokens_token_code", table_name="child_tokens")
    op.drop_index("ix_child_tokens_child_id", table_name="child_tokens")
    op.drop_table("child_tokens")
    op.drop_table("children")