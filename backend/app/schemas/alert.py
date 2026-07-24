"""Alert Pydantic Schemas - Alert & Notification System"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    """Internal schema for creating alerts (not exposed via API)."""
    incident_id: str
    matched_incident_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1000)
    source: str = "system"
    extra_data: Optional[dict] = None


class AlertUpdate(BaseModel):
    """Schema for alert status transitions."""
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    dismissed_by: Optional[str] = None


class AlertResponse(BaseModel):
    """Full alert response."""
    id: str
    incident_id: str
    matched_incident_id: Optional[str] = None
    alert_type: str
    severity: str
    status: str
    title: str
    description: str
    source: str
    extra_data: Optional[dict] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    """Paginated alert list."""
    alerts: list[AlertResponse]
    total: int
    skip: int
    limit: int


class AlertSummaryResponse(BaseModel):
    """Alert counts by severity and status."""
    total_open: int = 0
    total_acknowledged: int = 0
    total_resolved: int = 0
    total_dismissed: int = 0
    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}