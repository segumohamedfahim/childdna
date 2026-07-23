"""QR Service - QR Code Generation Business Logic"""
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.child_token import ChildToken
from app.models.enums import TokenStatus
from app.repositories.child_token import ChildTokenRepository
from app.core.exceptions import (
    TokenNotFound,
    TokenNotActiveForQR,
    TokenAlreadyRevoked,
    TokenExpired,
    InvalidTokenFormat,
    QRGenerationFailed,
)
from app.utils.token_generator import validate_format
from app.utils.qr_generator import generate_svg, generate_png


@dataclass
class QRResult:
    """Typed result from QR code generation."""

    content: bytes
    media_type: str
    filename: str


class QRService:
    """Service for generating QR codes from child DNA tokens.

    Validates token state and delegates image generation to the
    QR code generator utility.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ChildTokenRepository(session)

    async def generate_qr(
        self,
        token_code: str,
        format: str = "svg",
        size: int = 300,
    ) -> QRResult:
        """Generate a QR code image for a child DNA token.

        Args:
            token_code: The child DNA token code to encode.
            format: Output image format ('svg' or 'png').
            size: Image dimension in pixels.

        Returns:
            QRResult: A dataclass containing image bytes, media type,
                and suggested filename.

        Raises:
            InvalidTokenFormat: If the token code format is invalid.
            TokenNotFound: If the token does not exist.
            TokenNotActiveForQR: If the token is not in ISSUED or ACTIVE
                status.
            TokenAlreadyRevoked: If the token has been revoked.
            TokenExpired: If the token has expired.
            QRGenerationFailed: If image generation fails unexpectedly.
        """
        # Validate token format
        if not validate_format(token_code):
            raise InvalidTokenFormat(token_code=token_code)

        # Fetch token
        token = await self.repository.get_by_token_code(token_code)
        if not token:
            raise TokenNotFound(token_code=token_code)

        # Validate token lifecycle status
        self._validate_token_status(token)

        # Generate QR image
        try:
            return self._generate_image(token_code, format, size)
        except (ImportError, ValueError, OSError) as exc:
            raise QRGenerationFailed(str(exc))

    def _validate_token_status(self, token: ChildToken) -> None:
        """Validate that the token is in a QR-generable state.

        Args:
            token: The child token model instance.

        Raises:
            TokenAlreadyRevoked: If token is revoked.
            TokenExpired: If token is expired.
            TokenNotActiveForQR: If token is not ISSUED or ACTIVE.
        """
        if token.status == TokenStatus.REVOKED:
            raise TokenAlreadyRevoked(token_code=token.token_code)

        if token.status == TokenStatus.EXPIRED:
            raise TokenExpired(token_code=token.token_code)

        if token.status not in (TokenStatus.ISSUED, TokenStatus.ACTIVE):
            raise TokenNotActiveForQR(token_code=token.token_code)

    def _generate_image(
        self,
        token_code: str,
        format: str,
        size: int,
    ) -> QRResult:
        """Generate QR image in the requested format.

        Args:
            token_code: The token code to encode.
            format: Output format ('svg' or 'png').
            size: Image dimension in pixels.

        Returns:
            QRResult: Generated image with metadata.
        """
        if format == "png":
            image_bytes = generate_png(token_code, size)
            media_type = "image/png"
        else:
            svg_str = generate_svg(token_code, size)
            image_bytes = svg_str.encode("utf-8")
            media_type = "image/svg+xml"

        extension = "png" if format == "png" else "svg"
        filename = f"{token_code}.{extension}"

        return QRResult(
            content=image_bytes,
            media_type=media_type,
            filename=filename,
        )