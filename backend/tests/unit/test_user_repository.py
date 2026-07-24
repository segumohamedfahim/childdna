"""Unit Tests for User Repository"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User


class TestUserRepository:
    """Test cases for UserRepository"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def user_repository(self, mock_session: AsyncMock) -> UserRepository:
        """Create UserRepository with mock session"""
        return UserRepository(mock_session)

    def test_get_by_email_found(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test get_by_email returns user when found"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_user.email = "test@example.com"
            mock_user.id = "test-id"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(
                return_value=mock_user
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.get_by_email("test@example.com")

            # Assert
            assert result is not None
            assert result.email == "test@example.com"

        anyio.run(run_test)

    def test_get_by_email_not_found(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test get_by_email returns None when not found"""
        async def run_test():
            # Arrange
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.get_by_email(
                "nonexistent@example.com"
            )

            # Assert
            assert result is None

        anyio.run(run_test)

    def test_get_by_guardian_id_found(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test get_by_guardian_id returns user when found"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_user.guardian_id = "guardian-id"
            mock_user.id = "test-id"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(
                return_value=mock_user
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.get_by_guardian_id(
                "guardian-id"
            )

            # Assert
            assert result is not None
            assert result.guardian_id == "guardian-id"

        anyio.run(run_test)

    def test_email_exists_true(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test email_exists returns True when email is taken"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(
                return_value=mock_user
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.email_exists(
                "existing@example.com"
            )

            # Assert
            assert result is True

        anyio.run(run_test)

    def test_email_exists_false(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test email_exists returns False when email is available"""
        async def run_test():
            # Arrange
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.email_exists(
                "new@example.com"
            )

            # Assert
            assert result is False

        anyio.run(run_test)

    def test_update_last_login(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test update_last_login sets the timestamp"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_user.last_login_at = None
            user_repository.get_by_id = AsyncMock(return_value=mock_user)

            # Act
            await user_repository.update_last_login("test-id")

            # Assert
            assert mock_user.last_login_at is not None
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_verify_email_updates_flag(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test verify_email sets email_verified to True"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_user.email_verified = False
            user_repository.get_by_id = AsyncMock(return_value=mock_user)

            # Act
            result = await user_repository.verify_email("test-id")

            # Assert
            assert result is not None
            assert result.email_verified is True
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_verify_email_not_found(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test verify_email returns None when user not found"""
        async def run_test():
            # Arrange
            user_repository.get_by_id = AsyncMock(return_value=None)

            # Act
            result = await user_repository.verify_email(
                "nonexistent-id"
            )

            # Assert
            assert result is None

        anyio.run(run_test)

    def test_get_by_id_from_base(
        self, user_repository: UserRepository, mock_session: AsyncMock
    ) -> None:
        """Test inherited get_by_id works"""
        async def run_test():
            # Arrange
            mock_user = MagicMock(spec=User)
            mock_user.id = "test-id"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(
                return_value=mock_user
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await user_repository.get_by_id("test-id")

            # Assert
            assert result is not None
            assert result.id == "test-id"

        anyio.run(run_test)