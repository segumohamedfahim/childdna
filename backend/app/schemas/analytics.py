"""Analytics Schemas - Aggregated Operational Insights"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnalyticsMetadata(BaseModel):
    """Metadata for analytics responses."""
    generated_at: datetime
    version: str = "1.0"


class DashboardStatisticsResponse(BaseModel):
    """Aggregated dashboard statistics."""
    metadata: AnalyticsMetadata
    total_children: int = 0
    total_guardians: int = 0
    total_incidents: int = 0
    total_matches: int = 0
    total_rescue_sessions: int = 0
    total_reunions: int = 0
    total_alerts: int = 0
    total_notifications: int = 0

    model_config = ConfigDict(from_attributes=True)


class RescueStatisticsResponse(BaseModel):
    """Rescue operation statistics."""
    metadata: AnalyticsMetadata
    active_rescues: int = 0
    completed_rescues: int = 0
    failed_rescues: int = 0
    average_rescue_duration: Optional[float] = None
    median_rescue_duration: Optional[float] = None
    success_rate: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class IncidentStatisticsResponse(BaseModel):
    """Incident analysis statistics."""
    metadata: AnalyticsMetadata
    total_incidents: int = 0
    open_incidents: int = 0
    resolved_incidents: int = 0
    average_confidence: float = 0.0
    severity_distribution: dict[str, int] = {}

    model_config = ConfigDict(from_attributes=True)


class MatchStatisticsResponse(BaseModel):
    """Incident match statistics."""
    metadata: AnalyticsMetadata
    total_matches: int = 0
    confirmed_matches: int = 0
    rejected_matches: int = 0
    pending_matches: int = 0
    average_match_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class AlertStatisticsResponse(BaseModel):
    """Alert system statistics."""
    metadata: AnalyticsMetadata
    total_alerts: int = 0
    active_alerts: int = 0
    acknowledged_alerts: int = 0
    resolved_alerts: int = 0
    dismissed_alerts: int = 0
    severity_distribution: dict[str, int] = {}

    model_config = ConfigDict(from_attributes=True)


class ReunionStatisticsResponse(BaseModel):
    """Reunion statistics."""
    metadata: AnalyticsMetadata
    completed_reunions: int = 0
    pending_reunions: int = 0
    average_time_to_reunion: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class GuardianStatisticsResponse(BaseModel):
    """Guardian statistics."""
    metadata: AnalyticsMetadata
    total_guardians: int = 0
    guardians_with_children: int = 0
    average_children_per_guardian: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ChildStatisticsResponse(BaseModel):
    """Child statistics."""
    metadata: AnalyticsMetadata
    total_children: int = 0
    active_cases: int = 0
    reunited_children: int = 0
    average_age: Optional[float] = None
    gender_distribution: dict[str, int] = {}

    model_config = ConfigDict(from_attributes=True)


class SystemHealthResponse(BaseModel):
    """System health status."""
    metadata: AnalyticsMetadata
    database_status: str = "unknown"
    ai_modules_available: bool = False
    report_engine_status: str = "unknown"
    authentication_status: str = "unknown"
    analytics_status: str = "operational"

    model_config = ConfigDict(from_attributes=True)