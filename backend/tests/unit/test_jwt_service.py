"""Unit Tests for JWT Service"""
import pytest
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from app.services.jwt_service import JWTService
from app.config.settings import settings


class TestJWTService:
    """Test cases for JWTService"""

    @pytest.fixture
    def jwt_service(self) -> JWTService:
        """Create JWTService"""
        return JWTService()

    def test_create_access_token_returns_string(
        self, jwt_service: JWTService
    ) -> None:
        """Test that create_access_token returns a non-empty string"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_two_parts(
        self, jwt_service: JWTService
    ) -> None:
        """Test that JWT has three dot-separated parts"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
        )
        parts = token.split(".")
        assert len(parts) == 3

    def test_decode_access_token_returns_correct_payload(
        self, jwt_service: JWTService
    ) -> None:
        """Test that decoded token contains correct claims"""
        user_id = "test-user-id"
        role = "guardian"
        token = jwt_service.create_access_token(
            user_id=user_id,
            role=role,
        )
        payload = jwt_service.decode_access_token(token)
        assert payload["sub"] == user_id
        assert payload["role"] == role
        assert payload["type"] == "access"

    def test_decode_access_token_contains_timestamps(
        self, jwt_service: JWTService
    ) -> None:
        """Test that decoded token has iat and exp claims"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
        )
        payload = jwt_service.decode_access_token(token)
        assert "iat" in payload
        assert "exp" in payload
        assert isinstance(payload["iat"], int)
        assert isinstance(payload["exp"], int)

    def test_decode_access_token_expiry_is_in_future(
        self, jwt_service: JWTService
    ) -> None:
        """Test that token expiry is in the future"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
        )
        payload = jwt_service.decode_access_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert exp > datetime.now(timezone.utc)

    def test_decode_access_token_expiry_matches_config(
        self, jwt_service: JWTService
    ) -> None:
        """Test that token expiry matches configured duration"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
        )
        payload = jwt_service.decode_access_token(token)
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_duration = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        actual_duration = exp - iat

        # Allow 1 second tolerance for rounding
        assert abs(actual_duration - expected_duration).total_seconds() < 2

    def test_decode_invalid_token_raises_exception(
        self, jwt_service: JWTService
    ) -> None:
        """Test that decoding an invalid token raises InvalidTokenError"""
        with pytest.raises(pyjwt.InvalidTokenError):
            jwt_service.decode_access_token("invalid-token-string")

    def test_decode_expired_token_raises_exception(
        self, jwt_service: JWTService
    ) -> None:
        """Test that decoding an expired token raises ExpiredSignatureError"""
        # Create an expired token by manipulating the payload
        now = datetime.now(timezone.utc)
        expire = now - timedelta(hours=1)  # 1 hour in the past
        payload = {
            "sub": "test-user-id",
            "role": "guardian",
            "iat": now - timedelta(hours=2),
            "exp": expire,
            "type": "access",
        }
        expired_token = pyjwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(pyjwt.ExpiredSignatureError):
            jwt_service.decode_access_token(expired_token)

    def test_create_access_token_with_additional_claims(
        self, jwt_service: JWTService
    ) -> None:
        """Test that additional claims are included in the token"""
        token = jwt_service.create_access_token(
            user_id="test-user-id",
            role="guardian",
            additional_claims={"guardian_id": "guardian-123"},
        )
        payload = jwt_service.decode_access_token(token)
        assert payload["guardian_id"] == "guardian-123"

    def test_get_token_expiry_returns_future_datetime(
        self, jwt_service: JWTService
    ) -> None:
        """Test that get_token_expiry returns a future datetime"""
        expiry = jwt_service.get_token_expiry()
        assert isinstance(expiry, datetime)
        assert expiry > datetime.now(timezone.utc)