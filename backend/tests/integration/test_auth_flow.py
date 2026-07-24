"""Integration Tests for Authentication Flow"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import anyio
from app.services.auth_service import AuthService
from app.services.password_service import PasswordService
from app.schemas.user import (
    UserCreate,
    UserLoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from app.core.exceptions import (
    InvalidCredentials,
    InvalidToken,
    UserNotActive,
    EmailAlreadyExists,
    PasswordTooWeak,
    RefreshTokenExpired,
    RefreshTokenRevoked,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken


class TestAuthFlow:
    """Integration-style tests for the complete authentication flow.

    Tests the full lifecycle: register -> login -> me -> refresh ->
    old token rejected -> logout -> refresh rejected.
    """

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def auth_service(self, mock_session: AsyncMock) -> AuthService:
        return AuthService(mock_session)

    @pytest.fixture
    def mock_user(self) -> MagicMock:
        user = MagicMock(spec=User)
        user.id = "test-user-id"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.phone = "1234567890"
        user.role = "guardian"
        user.is_active = True
        user.email_verified = False
        user.last_login_at = None
        user.guardian_id = None
        user.password_hash = PasswordService().hash_password("Test@1234")
        return user

    def test_full_auth_flow(
        self, auth_service: AuthService, mock_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test complete auth lifecycle: register -> login -> me -> refresh -> logout."""
        async def run_test():
            import hashlib
            from datetime import datetime, timedelta, timezone
            from app.schemas.user import UserResponse

            # Step 1: Register
            register_data = UserCreate(
                email="new@example.com",
                password="Test@1234",
                full_name="New User",
            )
            auth_service.user_repo.email_exists = AsyncMock(return_value=False)
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            # Mock UserResponse.model_validate to avoid DB-dependent validation
            mock_response = UserResponse(
                id="new-user-id",
                email="new@example.com",
                full_name="New User",
                role="guardian",
                is_active=True,
                email_verified=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            with patch(
                "app.services.auth_service.UserResponse.model_validate",
                return_value=mock_response,
            ):
                result = await auth_service.register(register_data)
            assert result.email == "new@example.com"

            # Step 2: Login
            login_data = UserLoginRequest(
                email="test@example.com",
                password="Test@1234",
            )
            auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)
            auth_service.user_repo.update_last_login = AsyncMock()
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()

            login_result = await auth_service.login(login_data)
            assert login_result.access_token is not None
            assert login_result.refresh_token is not None
            assert login_result.token_type == "bearer"

            old_refresh_token = login_result.refresh_token

            # Step 3: Get current user
            auth_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
            user = await auth_service.get_current_user("test-user-id")
            assert user.email == "test@example.com"

            # Step 4: Refresh token
            old_token_hash = hashlib.sha256(
                old_refresh_token.encode("utf-8")
            ).hexdigest()

            mock_stored_token = MagicMock(spec=RefreshToken)
            mock_stored_token.user_id = mock_user.id
            mock_stored_token.token_hash = old_token_hash
            mock_stored_token.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            mock_stored_token.revoked = False

            refresh_data = RefreshTokenRequest(refresh_token=old_refresh_token)
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )
            auth_service.token_repo.revoke = AsyncMock()
            auth_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()

            refresh_result = await auth_service.refresh_token(refresh_data)
            assert refresh_result.access_token is not None
            assert refresh_result.refresh_token is not None
            assert refresh_result.refresh_token != old_refresh_token

            # Step 5: Old refresh token should be rejected (revoked)
            mock_stored_token.revoked = True
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )

            with pytest.raises(RefreshTokenRevoked):
                await auth_service.refresh_token(
                    RefreshTokenRequest(refresh_token=old_refresh_token)
                )

            # Step 6: Logout
            new_refresh_token = refresh_result.refresh_token
            new_token_hash = hashlib.sha256(
                new_refresh_token.encode("utf-8")
            ).hexdigest()

            mock_stored_token2 = MagicMock(spec=RefreshToken)
            mock_stored_token2.user_id = mock_user.id
            mock_stored_token2.token_hash = new_token_hash
            mock_stored_token2.expires_at = datetime.now(timezone.utc) + timedelta(days=30)

            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token2
            )
            auth_service.token_repo.revoke = AsyncMock()

            await auth_service.logout("test-user-id", new_refresh_token)
            auth_service.token_repo.revoke.assert_called_once_with(new_token_hash)

            # Step 7: Refresh after logout should fail
            mock_stored_token2.revoked = True
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token2
            )

            with pytest.raises(RefreshTokenRevoked):
                await auth_service.refresh_token(
                    RefreshTokenRequest(refresh_token=new_refresh_token)
                )

        anyio.run(run_test)

    def test_wrong_password(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test login with wrong password."""
        async def run_test():
            data = UserLoginRequest(
                email="test@example.com",
                password="WrongPass@1",
            )
            auth_service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

            with pytest.raises(InvalidCredentials):
                await auth_service.login(data)

        anyio.run(run_test)

    def test_duplicate_email(
        self, auth_service: AuthService
    ) -> None:
        """Test registration with duplicate email."""
        async def run_test():
            data = UserCreate(
                email="existing@example.com",
                password="Test@1234",
                full_name="Existing User",
            )
            auth_service.user_repo.email_exists = AsyncMock(return_value=True)

            with pytest.raises(EmailAlreadyExists):
                await auth_service.register(data)

        anyio.run(run_test)

    def test_expired_token(
        self, auth_service: AuthService
    ) -> None:
        """Test refresh with expired token."""
        async def run_test():
            import hashlib
            from datetime import datetime, timedelta, timezone

            token_str = "expired-token"
            token_hash = hashlib.sha256(
                token_str.encode("utf-8")
            ).hexdigest()

            mock_stored_token = MagicMock(spec=RefreshToken)
            mock_stored_token.token_hash = token_hash
            mock_stored_token.expires_at = (
                datetime.now(timezone.utc) - timedelta(days=1)
            )
            mock_stored_token.revoked = False

            data = RefreshTokenRequest(refresh_token=token_str)
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )

            with pytest.raises(RefreshTokenExpired):
                await auth_service.refresh_token(data)

        anyio.run(run_test)

    def test_invalid_token(
        self, auth_service: AuthService
    ) -> None:
        """Test refresh with invalid token."""
        async def run_test():
            data = RefreshTokenRequest(refresh_token="invalid-token")
            auth_service.token_repo.get_by_token_hash = AsyncMock(return_value=None)

            with pytest.raises(InvalidToken):
                await auth_service.refresh_token(data)

        anyio.run(run_test)