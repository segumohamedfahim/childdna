"""Report Schemas - Mission Report Response Models"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReportMetadata(BaseModel):
    """Metadata common to all reports."""
    generated_at: datetime
    report_type: str
    version: str = "1.0"


class IncidentReportResponse(BaseModel):
    """Report for a single incident analysis."""
    metadata: ReportMetadata
    incident_id: str
    incident_status: Optional[str] = None
    incident_priority: Optional[int] = None
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    analysis_summary: Optional[str] = None
    analysis_engine: Optional[str] = None
    overall_confidence: Optional[float] = None
    severity: Optional[str] = None
    recommendations: list[str] = []
    analysis_timestamp: Optional[datetime] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineEventItem(BaseModel):
    """A timeline event within a rescue report."""
    event_type: str
    description: str
    timestamp: datetime
    created_by: Optional[str] = None


class RescueReportResponse(BaseModel):
    """Report for a rescue session."""
    metadata: ReportMetadata
    rescue_id: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    rescuer_name: Optional[str] = None
    rescuer_phone: Optional[str] = None
    location_name: Optional[str] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    timeline: list[TimelineEventItem] = []
    outcome: Optional[str] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReunionReportResponse(BaseModel):
    """Report for a reunion record."""
    metadata: ReportMetadata
    reunion_id: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    guardian_name: Optional[str] = None
    rescuer_name: Optional[str] = None
    reunion_time: Optional[datetime] = None
    verification_method: Optional[str] = None
    remarks: Optional[str] = None
    verification_status: str = "verified"
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RescueHistoryItem(BaseModel):
    """A rescue session within a child report."""
    rescue_id: str
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    outcome: Optional[str] = None


class ChildReportResponse(BaseModel):
    """Report for a child's complete profile and history."""
    metadata: ReportMetadata
    child_id: str
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    status: Optional[str] = None
    guardian_id: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_email: Optional[str] = None
    guardian_phone: Optional[str] = None
    rescue_history: list[RescueHistoryItem] = []
    incident_count: int = 0
    reunion_count: int = 0
    timeline_summary: str = ""
    reunion_status: str = "unknown"
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemReportResponse(BaseModel):
    """Aggregated system-wide statistics report."""
    metadata: ReportMetadata
    total_children: int = 0
    total_guardians: int = 0
    total_tokens: int = 0
    active_rescues: int = 0
    completed_reunions: int = 0
    active_alerts: int = 0
    total_incidents: int = 0
    total_alert_open: int = 0
    total_alert_acknowledged: int = 0
    total_alert_resolved: int = 0
    total_alert_dismissed: int = 0
    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)