"""Notification Pydantic Schemas - Guardian Notifications"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Full notification response."""
    id: str
    guardian_id: str
    child_id: Optional[str] = None
    incident_id: Optional[str] = None
    notification_type: str
    channel: str
    status: str
    title: str
    message: str
    extra_data: Optional[dict] = None
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated notification list."""
    notifications: list[NotificationResponse]
    total: int
    skip: int
    limit: int


class NotificationSummaryResponse(BaseModel):
    """Notification counts for a guardian."""
    total_unread: int = 0
    total_sent: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}