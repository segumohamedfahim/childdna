"""ReunionRecord Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ReunionRecordBase(BaseModel):
    """Base ReunionRecord schema"""
    rescuer_name: str
    guardian_name: str
    reunion_time: datetime
    verification_method: str
    remarks: Optional[str] = None


class ReunionRecordCreate(ReunionRecordBase):
    """Schema for creating a ReunionRecord"""
    child_id: str


class ReunionRecordUpdate(BaseModel):
    """Schema for updating a ReunionRecord"""
    remarks: Optional[str] = None


class ReunionRecordResponse(ReunionRecordBase):
    """Schema for ReunionRecord response"""
    id: str
    child_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
