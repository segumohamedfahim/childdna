"""Guardian Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.guardian import GuardianStatus


class GuardianBase(BaseModel):
    """Base Guardian schema"""
    email: EmailStr
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    full_name: str
    address: Optional[str] = None
    preferred_language: str = "en"


class GuardianCreate(GuardianBase):
    """Schema for creating a Guardian"""
    pass


class GuardianUpdate(BaseModel):
    """Schema for updating a Guardian"""
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    preferred_language: Optional[str] = None
    is_active: Optional[bool] = None


class GuardianResponse(GuardianBase):
    """Schema for Guardian response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
