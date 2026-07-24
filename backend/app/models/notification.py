"""Notification Model - Guardian Notification"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from app.models.base import TimestampMixin


class Notification(TimestampMixin, Base):
    """Guardian notification for rescue events.

    Notifications are dispatched by rescue and reunion services when
    incidents change status or reunions are completed. Delivery
    is in-app only for this sprint; future sprints can add
    email/SMS channels.
    """
    __tablename__ = "notifications"

    guardian_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guardians.id"),
        nullable=False,
    )
    child_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=True,
    )
    incident_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rescue_sessions.id"),
        nullable=True,
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="in_app",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Indexes
    __table_args__ = (
        Index("ix_notifications_guardian_id", "guardian_id"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_created_at", "created_at"),
    )