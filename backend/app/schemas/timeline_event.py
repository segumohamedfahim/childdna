"""TimelineEvent Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.timeline_event import EventType


class TimelineEventBase(BaseModel):
    """Base TimelineEvent schema"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    event_type: EventType
    description: str
    created_by: Optional[str] = None


class TimelineEventCreate(TimelineEventBase):
    """Schema for creating a TimelineEvent"""
    child_id: str
    rescue_session_id: Optional[str] = None


class TimelineEventUpdate(BaseModel):
    """Schema for updating a TimelineEvent"""
    description: Optional[str] = None


class TimelineEventResponse(TimelineEventBase):
    """Schema for TimelineEvent response"""
    id: str
    child_id: str
    rescue_session_id: Optional[str] = None
    timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
