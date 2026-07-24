"""Unit Tests for Auth Service"""
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
    UserNotFound,
    UserNotActive,
    EmailAlreadyExists,
    PasswordTooWeak,
    RefreshTokenExpired,
    RefreshTokenRevoked,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken


class TestAuthService:
    """Test cases for AuthService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def auth_service(self, mock_session: AsyncMock) -> AuthService:
        """Create AuthService with mock session"""
        return AuthService(mock_session)

    @pytest.fixture
    def mock_user(self) -> MagicMock:
        """Create a mock user"""
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

    # --- register() tests ---

    def test_register_success(
        self, auth_service: AuthService, mock_session: AsyncMock
    ) -> None:
        """Test successful user registration"""
        async def run_test():
            from datetime import datetime, timezone
            from app.schemas.user import UserResponse

            data = UserCreate(
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
                result = await auth_service.register(data)

            assert result.email == "new@example.com"
            assert result.full_name == "New User"
            assert result.role == "guardian"

        anyio.run(run_test)

    def test_register_duplicate_email(
        self, auth_service: AuthService
    ) -> None:
        """Test registration with duplicate email raises exception"""
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

    def test_register_weak_password(
        self, auth_service: AuthService
    ) -> None:
        """Test registration with weak password raises exception"""
        async def run_test():
            # Password passes Pydantic min_length=8 but fails strength check
            data = UserCreate(
                email="test@example.com",
                password="abcdefgh",
                full_name="Test User",
            )

            with pytest.raises(PasswordTooWeak):
                await auth_service.register(data)

        anyio.run(run_test)

    # --- login() tests ---

    def test_login_success(
        self, auth_service: AuthService, mock_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test successful login returns tokens"""
        async def run_test():
            data = UserLoginRequest(
                email="test@example.com",
                password="Test@1234",
            )
            auth_service.user_repo.get_by_email = AsyncMock(
                return_value=mock_user
            )
            auth_service.user_repo.update_last_login = AsyncMock()
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()

            result = await auth_service.login(data)

            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.token_type == "bearer"
            assert result.expires_in > 0

        anyio.run(run_test)

    def test_login_invalid_email(
        self, auth_service: AuthService
    ) -> None:
        """Test login with invalid email raises exception"""
        async def run_test():
            data = UserLoginRequest(
                email="nonexistent@example.com",
                password="Test@1234",
            )
            auth_service.user_repo.get_by_email = AsyncMock(
                return_value=None
            )

            with pytest.raises(InvalidCredentials):
                await auth_service.login(data)

        anyio.run(run_test)

    def test_login_invalid_password(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test login with wrong password raises exception"""
        async def run_test():
            data = UserLoginRequest(
                email="test@example.com",
                password="WrongPass@1",
            )
            auth_service.user_repo.get_by_email = AsyncMock(
                return_value=mock_user
            )

            with pytest.raises(InvalidCredentials):
                await auth_service.login(data)

        anyio.run(run_test)

    def test_login_inactive_user(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test login with inactive user raises exception"""
        async def run_test():
            mock_user.is_active = False
            data = UserLoginRequest(
                email="test@example.com",
                password="Test@1234",
            )
            auth_service.user_repo.get_by_email = AsyncMock(
                return_value=mock_user
            )

            with pytest.raises(UserNotActive):
                await auth_service.login(data)

        anyio.run(run_test)

    # --- refresh_token() tests ---

    def test_refresh_token_success(
        self, auth_service: AuthService, mock_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test successful token refresh"""
        async def run_test():
            from datetime import datetime, timedelta, timezone
            import hashlib

            old_token_str = "test-refresh-token"
            old_token_hash = hashlib.sha256(
                old_token_str.encode("utf-8")
            ).hexdigest()

            mock_stored_token = MagicMock(spec=RefreshToken)
            mock_stored_token.user_id = mock_user.id
            mock_stored_token.token_hash = old_token_hash
            mock_stored_token.expires_at = (
                datetime.now(timezone.utc) + timedelta(days=30)
            )
            mock_stored_token.revoked = False

            data = RefreshTokenRequest(refresh_token=old_token_str)
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )
            auth_service.token_repo.revoke = AsyncMock()
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_user
            )
            mock_session.add = MagicMock()
            mock_session.commit = AsyncMock()

            result = await auth_service.refresh_token(data)

            assert result.access_token is not None
            assert result.refresh_token is not None
            assert result.refresh_token != old_token_str

        anyio.run(run_test)

    def test_refresh_token_not_found(
        self, auth_service: AuthService
    ) -> None:
        """Test refresh with invalid token raises exception"""
        async def run_test():
            data = RefreshTokenRequest(refresh_token="invalid-token")
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=None
            )

            with pytest.raises(InvalidToken):
                await auth_service.refresh_token(data)

        anyio.run(run_test)

    def test_refresh_token_expired(
        self, auth_service: AuthService
    ) -> None:
        """Test refresh with expired token raises exception"""
        async def run_test():
            from datetime import datetime, timedelta, timezone
            import hashlib

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

    def test_refresh_token_revoked(
        self, auth_service: AuthService
    ) -> None:
        """Test refresh with revoked token raises exception"""
        async def run_test():
            from datetime import datetime, timedelta, timezone
            import hashlib

            token_str = "revoked-token"
            token_hash = hashlib.sha256(
                token_str.encode("utf-8")
            ).hexdigest()

            mock_stored_token = MagicMock(spec=RefreshToken)
            mock_stored_token.token_hash = token_hash
            mock_stored_token.expires_at = (
                datetime.now(timezone.utc) + timedelta(days=30)
            )
            mock_stored_token.revoked = True

            data = RefreshTokenRequest(refresh_token=token_str)
            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )

            with pytest.raises(RefreshTokenRevoked):
                await auth_service.refresh_token(data)

        anyio.run(run_test)

    # --- logout() tests ---

    def test_logout_revokes_token(
        self, auth_service: AuthService
    ) -> None:
        """Test logout revokes the provided refresh token"""
        async def run_test():
            import hashlib
            token_str = "test-refresh-token"
            token_hash = hashlib.sha256(
                token_str.encode("utf-8")
            ).hexdigest()

            mock_stored_token = MagicMock(spec=RefreshToken)
            mock_stored_token.user_id = "test-user-id"

            auth_service.token_repo.get_by_token_hash = AsyncMock(
                return_value=mock_stored_token
            )
            auth_service.token_repo.revoke = AsyncMock()

            await auth_service.logout("test-user-id", token_str)
            auth_service.token_repo.revoke.assert_called_once_with(
                token_hash
            )

        anyio.run(run_test)

    # --- logout_all() tests ---

    def test_logout_all_revokes_all(
        self, auth_service: AuthService
    ) -> None:
        """Test logout_all revokes all refresh tokens"""
        async def run_test():
            auth_service.token_repo.revoke_all_for_user = AsyncMock(
                return_value=3
            )

            count = await auth_service.logout_all("test-user-id")

            assert count == 3
            auth_service.token_repo.revoke_all_for_user.assert_called_once_with(
                "test-user-id"
            )

        anyio.run(run_test)

    # --- get_current_user() tests ---

    def test_get_current_user_found(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test get_current_user returns user when found"""
        async def run_test():
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_user
            )

            result = await auth_service.get_current_user("test-user-id")

            assert result.id == "test-user-id"
            assert result.email == "test@example.com"

        anyio.run(run_test)

    def test_get_current_user_not_found(
        self, auth_service: AuthService
    ) -> None:
        """Test get_current_user raises exception when not found"""
        async def run_test():
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=None
            )

            with pytest.raises(UserNotFound):
                await auth_service.get_current_user("nonexistent-id")

        anyio.run(run_test)

    # --- change_password() tests ---

    def test_change_password_success(
        self, auth_service: AuthService, mock_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test successful password change"""
        async def run_test():
            data = ChangePasswordRequest(
                current_password="Test@1234",
                new_password="NewPass@123",
            )
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_user
            )
            mock_session.commit = AsyncMock()

            await auth_service.change_password("test-user-id", data)
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_change_password_wrong_current(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test password change with wrong current password"""
        async def run_test():
            data = ChangePasswordRequest(
                current_password="WrongPass@1",
                new_password="NewPass@123",
            )
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_user
            )

            with pytest.raises(InvalidCredentials):
                await auth_service.change_password("test-user-id", data)

        anyio.run(run_test)

    def test_change_password_weak_new(
        self, auth_service: AuthService, mock_user: MagicMock
    ) -> None:
        """Test password change with weak new password"""
        async def run_test():
            # Password passes Pydantic min_length=8 but fails strength check
            data = ChangePasswordRequest(
                current_password="Test@1234",
                new_password="abcdefgh",
            )
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_user
            )

            with pytest.raises(PasswordTooWeak):
                await auth_service.change_password("test-user-id", data)

        anyio.run(run_test)

    def test_change_password_user_not_found(
        self, auth_service: AuthService
    ) -> None:
        """Test password change with non-existent user"""
        async def run_test():
            data = ChangePasswordRequest(
                current_password="Test@1234",
                new_password="NewPass@123",
            )
            auth_service.user_repo.get_by_id = AsyncMock(
                return_value=None
            )

            with pytest.raises(UserNotFound):
                await auth_service.change_password("nonexistent-id", data)

        anyio.run(run_test)