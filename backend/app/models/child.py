"""Child Model - Child Entity for Safety Registration"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Date, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin
from app.models.enums import ChildStatus


class Child(TimestampMixin, Base):
    """Child entity for safety registration"""
    __tablename__ = "children"
    
    guardian_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guardians.id"),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    blood_group: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    allergies: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    medical_notes: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )
    special_needs: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    status: Mapped[ChildStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=ChildStatus.ACTIVE.value,
    )
    
    # Relationships
    guardian: Mapped["Guardian"] = relationship(
        "Guardian",
        back_populates="children",
        lazy="selectin",
    )
    tokens: Mapped[list["ChildToken"]] = relationship(
        "ChildToken",
        back_populates="child",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    rescue_sessions: Mapped[list["RescueSession"]] = relationship(
        "RescueSession",
        back_populates="child",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(
        "TimelineEvent",
        back_populates="child",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    reunion_records: Mapped[list["ReunionRecord"]] = relationship(
        "ReunionRecord",
        back_populates="child",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_children_guardian_id", "guardian_id"),
    )
