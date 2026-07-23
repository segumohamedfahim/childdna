"""Child Pydantic Schemas"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.child import ChildStatus


class ChildBase(BaseModel):
    """Base Child schema"""
    full_name: str
    nickname: Optional[str] = None
    date_of_birth: date
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    special_needs: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    photo_url: Optional[str] = None


class ChildCreate(ChildBase):
    """Schema for creating a Child"""
    guardian_id: str


class ChildUpdate(BaseModel):
    """Schema for updating a Child"""
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None
    special_needs: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[ChildStatus] = None


class ChildResponse(ChildBase):
    """Schema for Child response"""
    id: str
    guardian_id: str
    status: ChildStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
