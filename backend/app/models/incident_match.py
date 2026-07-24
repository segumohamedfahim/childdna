"""IncidentMatch Model - Potential Match Between Rescue Incidents"""
from typing import Optional
from sqlalchemy import String, Float, Index, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class IncidentMatch(TimestampMixin, Base):
    """Potential match between two rescue incidents.

    Stores the result of comparing a source incident's analysis
    against a candidate incident's analysis. The AI only recommends;
    authorities always make the final merge decision.
    """
    __tablename__ = "incident_matches"

    incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rescue_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    matched_incident_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rescue_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    similarity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        server_default="0.0",
    )
    match_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="no_match",
    )
    recommendation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="no_action",
    )
    algorithm_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="rule_engine_v1",
    )
    score_breakdown: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    incident: Mapped["RescueSession"] = relationship(
        "RescueSession",
        foreign_keys=[incident_id],
        lazy="selectin",
    )
    matched_incident: Mapped["RescueSession"] = relationship(
        "RescueSession",
        foreign_keys=[matched_incident_id],
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (
        Index("ix_incident_matches_incident_id", "incident_id"),
        Index(
            "ix_incident_matches_incident_score",
            "incident_id",
            "similarity_score",
        ),
        Index(
            "ix_incident_matches_matched_incident_id",
            "matched_incident_id",
        ),
    )
