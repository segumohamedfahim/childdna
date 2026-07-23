"""RescueSession Model - Rescue Operation Session"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin
from app.models.enums import SessionStatus


class RescueSession(TimestampMixin, Base):
    """Rescue operation session for child safety"""
    __tablename__ = "rescue_sessions"
    
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=SessionStatus.PENDING.value,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="2",
    )
    rescuer_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    rescuer_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    location_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    child: Mapped["Child"] = relationship(
        "Child",
        back_populates="rescue_sessions",
        lazy="selectin",
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        "TimelineEvent",
        back_populates="rescue_session",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_rescue_sessions_child_id", "child_id"),
        Index("ix_rescue_sessions_status", "status"),
    )
