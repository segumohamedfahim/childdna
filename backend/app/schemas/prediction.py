"""Prediction Schemas - AI Intelligence Prediction Models"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PredictionMetadata(BaseModel):
    """Metadata for prediction responses."""
    generated_at: datetime
    model_version: str = "heuristic_v1"
    engine: str = "deterministic"

    model_config = ConfigDict(protected_namespaces=())


class ReunionPredictionResponse(BaseModel):
    """Prediction for child reunion probability."""
    metadata: PredictionMetadata
    child_id: str
    reunion_probability: float
    confidence: str
    factors: list[str] = []
    explanation: str = ""
    recommended_actions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class RescuePredictionResponse(BaseModel):
    """Prediction for rescue session success."""
    metadata: PredictionMetadata
    rescue_session_id: str
    success_probability: float
    confidence: str
    factors: list[str] = []
    explanation: str = ""
    recommended_actions: list[str] = []
    estimated_completion_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class IncidentRiskResponse(BaseModel):
    """Risk assessment for a child."""
    metadata: PredictionMetadata
    child_id: str
    risk_level: str
    risk_score: float
    factors: list[str] = []
    explanation: str = ""
    recommended_actions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class AlertPredictionResponse(BaseModel):
    """Prediction for alert generation probability."""
    metadata: PredictionMetadata
    incident_analysis_id: str
    alert_probability: float
    confidence: str
    factors: list[str] = []
    explanation: str = ""
    recommended_actions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class PriorityPredictionResponse(BaseModel):
    """Priority score for an incident analysis."""
    metadata: PredictionMetadata
    incident_analysis_id: str
    priority_score: float
    priority_level: str
    factors: list[str] = []
    explanation: str = ""
    recommended_actions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class AIModelStatus(BaseModel):
    """Status of a single AI module."""
    name: str
    status: str
    version: str


class AISummarySection(BaseModel):
    """A section within an AI summary."""
    heading: str
    content: str


class AISummaryResponse(BaseModel):
    """Structured AI-generated summary."""
    metadata: PredictionMetadata
    summary_type: str
    entity_id: str
    overall_assessment: str = ""
    key_observations: list[str] = []
    potential_concerns: list[str] = []
    confidence_level: str = ""
    recommended_next_actions: list[str] = []
    sections: list[AISummarySection] = []

    model_config = ConfigDict(from_attributes=True)


class RecommendationItem(BaseModel):
    """A single recommendation from the AI engine."""
    recommendation: str
    priority: str
    reason: str
    confidence: float


class RecommendationResponse(BaseModel):
    """Response containing AI recommendations."""
    metadata: PredictionMetadata
    entity_id: str
    entity_type: str
    recommendations: list[RecommendationItem] = []

    model_config = ConfigDict(from_attributes=True)


class PredictionHealthResponse(BaseModel):
    """Health status of the prediction AI platform."""
    metadata: PredictionMetadata
    prediction_engine_status: str = "operational"
    recommendation_engine_status: str = "operational"
    summary_engine_status: str = "operational"
    ai_version: str = "1.0"
    supported_modules: list[str] = [
        "reunion_prediction",
        "rescue_prediction",
        "incident_risk",
        "alert_prediction",
        "priority_scoring",
        "ai_summary",
        "recommendation_engine",
        "system_health",
    ]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)