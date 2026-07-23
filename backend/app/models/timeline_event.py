"""TimelineEvent Model - Event in Rescue Timeline"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin
from app.models.enums import EventType


class TimelineEvent(TimestampMixin, Base):
    """Event in the rescue timeline"""
    __tablename__ = "timeline_events"
    
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
    )
    rescue_session_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rescue_sessions.id"),
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
    event_type: Mapped[EventType] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    
    # Relationships
    child: Mapped["Child"] = relationship(
        "Child",
        back_populates="timeline_events",
        lazy="selectin",
    )
    rescue_session: Mapped["RescueSession"] = relationship(
        "RescueSession",
        back_populates="timeline_events",
        lazy="selectin",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_timeline_events_child_id", "child_id"),
        Index("ix_timeline_events_rescue_session_id", "rescue_session_id"),
        Index("ix_timeline_events_event_type", "event_type"),
    )
