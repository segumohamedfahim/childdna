"""RescueSession Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.rescue_session import SessionStatus


class RescueSessionBase(BaseModel):
    """Base RescueSession schema"""
    priority: int = 2
    rescuer_name: Optional[str] = None
    rescuer_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    notes: Optional[str] = None


class RescueSessionCreate(RescueSessionBase):
    """Schema for creating a RescueSession"""
    child_id: str


class RescueSessionUpdate(BaseModel):
    """Schema for updating a RescueSession"""
    status: Optional[SessionStatus] = None
    priority: Optional[int] = None
    rescuer_name: Optional[str] = None
    rescuer_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    notes: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class RescueSessionResponse(RescueSessionBase):
    """Schema for RescueSession response"""
    id: str
    child_id: str
    status: SessionStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
