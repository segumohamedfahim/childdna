"""Scanner Pydantic Schemas - Token Lookup API"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import TokenStatus


class ScannerLookupRequest(BaseModel):
    """Request schema for scanner token lookup."""
    token_code: str


class ScannerLookupResponse(BaseModel):
    """Public rescue information returned to scanner.

    Contains only safe fields. No IDs, qr_secret, email, address,
    medical data, or audit information are exposed.
    """
    child_name: str
    child_age: int = Field(ge=0, le=150)
    child_gender: Optional[str] = None
    guardian_name: str
    guardian_phone: Optional[str] = None
    token_status: TokenStatus
    last_scanned_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)