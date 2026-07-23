"""Token Generator Utility - Secure Token Generation for Child DNA"""
import secrets
from typing import Final
from app.config.settings import settings


# Character set: uppercase alphanumeric, excluding ambiguous characters
TOKEN_CHARS: Final[str] = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate() -> str:
    """Generate a secure random token in DNA-XXXX-XXXX format.
    
    Returns:
        str: A unique token code in the format DNA-XXXX-XXXX
    """
    segment = _generate_segment
    return f"{settings.TOKEN_PREFIX}{settings.TOKEN_SEPARATOR}{segment()}{settings.TOKEN_SEPARATOR}{segment()}"


def _generate_segment() -> str:
    """Generate a single token segment.
    
    Returns:
        str: A random segment of TOKEN_SEGMENT_LENGTH characters
    """
    return "".join(secrets.choice(TOKEN_CHARS) for _ in range(settings.TOKEN_SEGMENT_LENGTH))


def validate_format(token_code: str) -> bool:
    """Validate that a token matches the expected DNA-XXXX-XXXX format.
    
    Args:
        token_code: The token code to validate
        
    Returns:
        bool: True if the token format is valid, False otherwise
    """
    if not token_code:
        return False
    
    parts = token_code.split(settings.TOKEN_SEPARATOR)
    if len(parts) != 3:
        return False
    
    prefix, segment1, segment2 = parts
    if prefix != settings.TOKEN_PREFIX:
        return False
    
    if len(segment1) != settings.TOKEN_SEGMENT_LENGTH:
        return False
    
    if len(segment2) != settings.TOKEN_SEGMENT_LENGTH:
        return False
    
    for char in segment1 + segment2:
        if char not in TOKEN_CHARS:
            return False
    
    return True