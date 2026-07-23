"""QR Code Generator Utility - Stateless QR Image Generation"""
import io
from typing import Final
import segno
from app.config.settings import settings

# QR payload prefix for scannable identification
QR_PAYLOAD_PREFIX: Final[str] = "childdna:"


def generate_svg(token_code: str, size: int = settings.DEFAULT_QR_SIZE) -> str:
    """Generate QR code as SVG string.

    Encodes the token code with a 'childdna:' prefix for scanner
    identification. SVG output is scalable and requires no raster
    image dependencies.

    Args:
        token_code: The child DNA token code to encode.
        size: Image dimension in pixels (used to compute scale).

    Returns:
        str: SVG XML string for the QR code.
    """
    scale = _compute_scale(size)
    qr = segno.make(_build_payload(token_code))
    return qr.svg_inline(scale=scale)


def generate_png(token_code: str, size: int = settings.DEFAULT_QR_SIZE) -> bytes:
    """Generate QR code as PNG bytes.

    Uses segno's native PNG output via save(). Pillow is not required
    for PNG generation with the default backend.

    Args:
        token_code: The child DNA token code to encode.
        size: Image dimension in pixels.

    Returns:
        bytes: PNG image bytes.
    """
    scale = _compute_scale(size)
    qr = segno.make(_build_payload(token_code))
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=scale)
    return buffer.getvalue()


def _build_payload(token_code: str) -> str:
    """Build the scannable QR payload string.

    Args:
        token_code: The child DNA token code.

    Returns:
        str: Payload string in 'childdna:DNA-XXXX-XXXX' format.
    """
    return f"{QR_PAYLOAD_PREFIX}{token_code}"


def _compute_scale(size: int) -> int:
    """Compute QR scale factor from requested pixel dimension.

    QR modules are 25 per side for standard v2 codes. Scale is
    clamped to produce a reasonable module count.

    Args:
        size: Requested image dimension in pixels.

    Returns:
        int: Scale factor for QR module rendering.
    """
    return max(1, size // 25)