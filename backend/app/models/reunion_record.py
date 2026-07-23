"""ReunionRecord Model - Child Reunion Record"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class ReunionRecord(TimestampMixin, Base):
    """Record of child reunion with guardian"""
    __tablename__ = "reunion_records"
    
    child_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
    )
    rescuer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    guardian_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    reunion_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    verification_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    remarks: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )
    
    # Relationships
    child: Mapped["Child"] = relationship(
        "Child",
        back_populates="reunion_records",
        lazy="selectin",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_reunion_records_child_id", "child_id"),
    )
