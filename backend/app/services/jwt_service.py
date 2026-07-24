"""JWT Service - Token Creation and Verification using PyJWT"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import jwt
from app.config.settings import settings


class JWTService:
    """Service for JWT access token creation and verification.

    Uses the existing JWT configuration from settings.py.
    Access tokens are short-lived (default 30 minutes).
    """

    def __init__(self) -> None:
        self.secret_key: str = settings.JWT_SECRET_KEY
        self.algorithm: str = settings.JWT_ALGORITHM
        self.access_token_expire_minutes: int = (
            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    def create_access_token(
        self,
        user_id: str,
        role: str,
        additional_claims: Optional[dict[str, Any]] = None,
    ) -> str:
        """Create a JWT access token for a user.

        Args:
            user_id: The user UUID.
            role: The user's role string.
            additional_claims: Optional extra claims to include in the token.

        Returns:
            str: The encoded JWT access token.
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload: dict[str, Any] = {
            "sub": user_id,
            "role": role,
            "iat": now,
            "exp": expire,
            "type": "access",
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT access token.

        Args:
            token: The JWT access token string.

        Returns:
            dict[str, Any]: The decoded token payload.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )

    def get_token_expiry(self) -> datetime:
        """Calculate the expiry datetime for a new access token.

        Returns:
            datetime: The expiry datetime in UTC.
        """
        return datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )