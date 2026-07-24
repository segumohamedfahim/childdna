"""IncidentMatch Pydantic Schemas - Matching Engine"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchRequest(BaseModel):
    """Request to run the matching engine for an incident.

    Optionally filter which candidate incidents to compare against.
    If candidate_incident_ids is omitted, all other incidents with
    analyses are used as candidates.
    """
    candidate_incident_ids: Optional[list[str]] = Field(
        default=None,
        description="Optional list of candidate incident UUIDs to compare against",
    )


class MatchResponse(BaseModel):
    """A single potential match result.

    Contains the matched incident ID, similarity score, category,
    recommendation, and detailed score breakdown.
    """
    matched_incident_id: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    match_category: str
    recommendation: str
    score_breakdown: Optional[dict] = None
    algorithm_version: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    """Response containing ranked match results for an incident."""
    incident_id: str
    matches: list[MatchResponse]
    total_matches: int
    algorithm_version: str


class CompareRequest(BaseModel):
    """Request to compare two specific analyses without persisting."""
    incident_id_a: str
    incident_id_b: str


class CompareResponse(BaseModel):
    """Response containing a single comparison result."""
    incident_id_a: str
    incident_id_b: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    match_category: str
    recommendation: str
    score_breakdown: Optional[dict] = None
    algorithm_version: str
