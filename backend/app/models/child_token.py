"""ChildToken Model - Digital Identity Token for Child"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Index, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import SoftDeleteMixin
from app.models.enums import TokenStatus


class ChildToken(SoftDeleteMixin, Base):
    """Digital identity token for child safety"""
    __tablename__ = "child_tokens"
    
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
    )
    token_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    qr_secret: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[TokenStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=TokenStatus.ACTIVE.value,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_scanned_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    child: Mapped["Child"] = relationship(
        "Child",
        back_populates="tokens",
        lazy="selectin",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_child_tokens_token_code", "token_code"),
        Index("ix_child_tokens_child_id", "child_id"),
    )