"""Scanner API Endpoint - Token Lookup for QR Scanner"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.scanner_service import ScannerService
from app.schemas.scanner import ScannerLookupRequest, ScannerLookupResponse

router = APIRouter(tags=["scanner"])


@router.post(
    "/scanner/lookup",
    response_model=ScannerLookupResponse,
    status_code=status.HTTP_200_OK,
    summary="Look up a child DNA token from QR scanner",
    description=(
        "Validates a scanned token code, verifies it is active and "
        "not expired or revoked, and returns safe public rescue "
        "information including child name, age, guardian contact."
    ),
)
async def scanner_lookup(
    lookup_data: ScannerLookupRequest,
    session: AsyncSession = Depends(get_db),
) -> ScannerLookupResponse:
    """Look up a child DNA token from a QR scanner."""
    service = ScannerService(session)
    return await service.lookup(lookup_data)