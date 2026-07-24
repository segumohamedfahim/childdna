"""Unit Tests for RefreshToken Repository"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
import anyio
from app.repositories.refresh_token import RefreshTokenRepository
from app.models.refresh_token import RefreshToken


class TestRefreshTokenRepository:
    """Test cases for RefreshTokenRepository"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def token_repository(
        self, mock_session: AsyncMock
    ) -> RefreshTokenRepository:
        """Create RefreshTokenRepository with mock session"""
        return RefreshTokenRepository(mock_session)

    def test_get_by_token_hash_found(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test get_by_token_hash returns token when found"""
        async def run_test():
            # Arrange
            mock_token = MagicMock(spec=RefreshToken)
            mock_token.token_hash = "abc123hash"
            mock_token.id = "token-id"

            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(
                return_value=mock_token
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await token_repository.get_by_token_hash(
                "abc123hash"
            )

            # Assert
            assert result is not None
            assert result.token_hash == "abc123hash"

        anyio.run(run_test)

    def test_get_by_token_hash_not_found(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test get_by_token_hash returns None when not found"""
        async def run_test():
            # Arrange
            mock_result = MagicMock()
            mock_result.scalar_one_or_none = MagicMock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await token_repository.get_by_token_hash(
                "nonexistent"
            )

            # Assert
            assert result is None

        anyio.run(run_test)

    def test_revoke_sets_revoked_flag(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test revoke sets revoked=True and revoked_at"""
        async def run_test():
            # Arrange
            mock_token = MagicMock(spec=RefreshToken)
            mock_token.revoked = False
            mock_token.revoked_at = None
            token_repository.get_by_token_hash = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await token_repository.revoke("abc123hash")

            # Assert
            assert result is not None
            assert result.revoked is True
            assert result.revoked_at is not None
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_revoke_not_found(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test revoke returns None when token not found"""
        async def run_test():
            # Arrange
            token_repository.get_by_token_hash = AsyncMock(
                return_value=None
            )

            # Act
            result = await token_repository.revoke("nonexistent")

            # Assert
            assert result is None

        anyio.run(run_test)

    def test_revoke_all_for_user(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test revoke_all_for_user revokes all active tokens"""
        async def run_test():
            # Arrange
            mock_token1 = MagicMock(spec=RefreshToken)
            mock_token1.revoked = False
            mock_token1.revoked_at = None

            mock_token2 = MagicMock(spec=RefreshToken)
            mock_token2.revoked = False
            mock_token2.revoked_at = None

            token_repository.get_active_by_user = AsyncMock(
                return_value=[mock_token1, mock_token2]
            )

            # Act
            count = await token_repository.revoke_all_for_user(
                "user-id"
            )

            # Assert
            assert count == 2
            assert mock_token1.revoked is True
            assert mock_token2.revoked is True
            assert mock_token1.revoked_at is not None
            assert mock_token2.revoked_at is not None
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_revoke_all_for_user_no_tokens(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test revoke_all_for_user returns 0 when no active tokens"""
        async def run_test():
            # Arrange
            token_repository.get_active_by_user = AsyncMock(
                return_value=[]
            )

            # Act
            count = await token_repository.revoke_all_for_user(
                "user-id"
            )

            # Assert
            assert count == 0
            mock_session.commit.assert_not_called()

        anyio.run(run_test)

    def test_cleanup_expired_deletes_old_tokens(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test cleanup_expired deletes expired tokens"""
        async def run_test():
            # Arrange
            mock_result = MagicMock()
            mock_result.rowcount = 3
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            count = await token_repository.cleanup_expired()

            # Assert
            assert count == 3
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_get_active_by_user_returns_only_active(
        self, token_repository: RefreshTokenRepository,
        mock_session: AsyncMock
    ) -> None:
        """Test get_active_by_user returns non-revoked, non-expired tokens"""
        async def run_test():
            # Arrange
            mock_token = MagicMock(spec=RefreshToken)
            mock_token.id = "active-token-id"
            mock_token.revoked = False

            mock_result = MagicMock()
            mock_result.scalars.return_value.all = MagicMock(
                return_value=[mock_token]
            )
            mock_session.execute = AsyncMock(return_value=mock_result)

            # Act
            result = await token_repository.get_active_by_user(
                "user-id"
            )

            # Assert
            assert len(result) == 1
            assert result[0].id == "active-token-id"

        anyio.run(run_test)