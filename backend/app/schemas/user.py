"""User and Auth Pydantic Schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user (registration)."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = "guardian"
    guardian_id: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Schema for user response (never exposes password_hash)."""
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    email_verified: bool
    last_login_at: Optional[datetime] = None
    guardian_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing an access token."""
    refresh_token: str = Field(..., min_length=1)


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)