"""IncidentAnalysis Model - Structured Intelligence from Rescue Reports"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, Index, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class IncidentAnalysis(TimestampMixin, Base):
    """Structured analysis output from the incident intelligence engine.

    Stores extracted attributes and confidence scores for a single
    rescue incident. One analysis per incident (enforced by unique FK).
    """
    __tablename__ = "incident_analyses"

    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rescue_sessions.id"),
        unique=True,
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    analysis_engine: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="rule_engine_v1",
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    gender_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    estimated_age_min: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    estimated_age_max: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    age_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    emotion: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    emotion_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    clothing: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    clothing_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    location_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    distinguishing_features: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    features_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    overall_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default="0.0",
    )

    # Relationships
    incident: Mapped["RescueSession"] = relationship(
        "RescueSession",
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_incident_analyses_incident_id", "incident_id", unique=True),
        Index("ix_incident_analyses_confidence", "overall_confidence"),
    )