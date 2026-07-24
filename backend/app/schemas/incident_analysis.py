"""IncidentAnalysis Pydantic Schemas - Intelligence Engine"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    """Request to analyze a rescue report."""
    notes: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Free-text rescue report to analyze",
    )


class AnalyzeResponse(BaseModel):
    """Structured analysis result from the intelligence engine.

    Contains extracted attributes and confidence scores. Designed to
    remain stable across engine implementations (rule-based, LLM, etc.).
    """
    incident_id: str
    raw_text: str
    analysis_engine: str = "rule_engine_v1"
    gender: Optional[str] = None
    gender_confidence: float = 0.0
    estimated_age_min: Optional[int] = None
    estimated_age_max: Optional[int] = None
    age_confidence: float = 0.0
    emotion: Optional[str] = None
    emotion_confidence: float = 0.0
    clothing: list[str] = []
    clothing_confidence: float = 0.0
    location: Optional[str] = None
    location_confidence: float = 0.0
    distinguishing_features: list[str] = []
    features_confidence: float = 0.0
    overall_confidence: float = Field(ge=0.0, le=1.0)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)