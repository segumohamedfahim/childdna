"""ChildToken Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.child_token import TokenStatus


class ChildTokenBase(BaseModel):
    """Base ChildToken schema"""
    token_code: str
    qr_secret: str
    expires_at: Optional[datetime] = None


class ChildTokenCreate(ChildTokenBase):
    """Schema for creating a ChildToken"""
    child_id: str


class ChildTokenUpdate(BaseModel):
    """Schema for updating a ChildToken"""
    status: Optional[TokenStatus] = None
    expires_at: Optional[datetime] = None


class ChildTokenResponse(ChildTokenBase):
    """Schema for ChildToken response"""
    id: str
    child_id: str
    status: TokenStatus
    issued_at: datetime
    last_scanned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
