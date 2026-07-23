"""QR Code API Endpoint - Child DNA Token QR Generation"""
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.qr_service import QRService
from app.config.settings import settings

router = APIRouter(tags=["qr"])


@router.get(
    "/tokens/{token_code}/qr",
    status_code=status.HTTP_200_OK,
    summary="Generate QR code for a child DNA token",
    description=(
        "Generates a QR code image for the specified child DNA token. "
        "The token must be in ISSUED or ACTIVE status. "
        "Supports SVG (default) and PNG output formats."
    ),
)
async def get_token_qr(
    token_code: str,
    format: str = Query(
        default="svg",
        pattern="^(svg|png)$",
        description="Output image format (svg or png)",
    ),
    download: bool = Query(
        default=False,
        description="If true, sets Content-Disposition to attachment",
    ),
    size: int = Query(
        default=settings.DEFAULT_QR_SIZE,
        ge=settings.MIN_QR_SIZE,
        le=settings.MAX_QR_SIZE,
        description="QR image dimension in pixels",
    ),
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Generate and return a QR code image for a child DNA token.

    Args:
        token_code: The child DNA token code to encode in the QR.
        format: Output image format ('svg' or 'png').
        download: Whether to force download via Content-Disposition.
        size: Image dimension in pixels (width and height).
        session: Database session from dependency injection.

    Returns:
        StreamingResponse: Streamed QR image with appropriate
            content type and optional download headers.
    """
    service = QRService(session)
    result = await service.generate_qr(
        token_code=token_code,
        format=format,
        size=size,
    )

    headers = {}
    if download:
        headers["Content-Disposition"] = (
            f'attachment; filename="{result.filename}"'
        )

    return StreamingResponse(
        content=iter([result.content]),
        media_type=result.media_type,
        headers=headers,
    )