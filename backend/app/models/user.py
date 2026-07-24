"""User Model - Authentication and Authorization Entity"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    """User entity for authentication and authorization.

    Maps to a system user who may be a guardian, authority figure,
    administrator, or scanner operator. Guardian users are linked
    to the existing Guardian business entity via guardian_id.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="guardian",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    guardian_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guardians.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    guardian: Mapped[Optional["Guardian"]] = relationship(
        "Guardian",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_guardian_id", "guardian_id"),
    )