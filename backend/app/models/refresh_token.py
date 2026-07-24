"""RefreshToken Model - JWT Refresh Token Storage"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class RefreshToken(TimestampMixin, Base):
    """Stored refresh token for JWT token rotation.

    Stores a SHA-256 hash of the refresh token (never the raw token).
    Tokens can be revoked individually or all at once for a user.
    Expired tokens should be cleaned up periodically.
    """
    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    device_info: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_refresh_tokens_user_id", "user_id"),
        Index("ix_refresh_tokens_token_hash", "token_hash"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )