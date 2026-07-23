"""Guardian Model - Parent/Guardian Entity"""
from typing import Optional
from sqlalchemy import String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import SoftDeleteMixin
from app.models.enums import GuardianStatus


class Guardian(SoftDeleteMixin, Base):
    """Guardian/Parent entity for child safety"""
    __tablename__ = "guardians"
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    alternate_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    preferred_language: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        server_default="en",
    )
    
    # Relationships
    children: Mapped[list["Child"]] = relationship(
        "Child",
        back_populates="guardian",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_guardians_email", "email"),
        Index("ix_guardians_phone", "phone"),
    )
