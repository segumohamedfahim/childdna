"""Integration Tests for Admin Flow"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.admin_service import AdminService
from app.schemas.user import UserResponse
from app.core.exceptions import UserNotFound, InsufficientPermissions
from app.models.user import User
from app.models.enums import UserRole


class TestAdminFlow:
    """Integration-style tests for admin operations."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def admin_service(self, mock_session: AsyncMock) -> AdminService:
        return AdminService(mock_session)

    @pytest.fixture
    def mock_admin_user(self) -> MagicMock:
        user = MagicMock(spec=User)
        user.id = "admin-id"
        user.email = "admin@example.com"
        user.full_name = "Admin User"
        user.role = "admin"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_guardian_user(self) -> MagicMock:
        from datetime import datetime, timezone
        user = MagicMock(spec=User)
        user.id = "guardian-id"
        user.email = "guardian@example.com"
        user.full_name = "Guardian User"
        user.phone = None
        user.role = "guardian"
        user.is_active = True
        user.email_verified = False
        user.last_login_at = None
        user.guardian_id = None
        user.created_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        return user

    def test_admin_can_list_users(
        self, admin_service: AdminService,
    ) -> None:
        """Test admin can list all users."""
        async def run_test():
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            mock_user1 = MagicMock(spec=User)
            mock_user1.id = "user-1"
            mock_user1.email = "user1@example.com"
            mock_user1.full_name = "User 1"
            mock_user1.phone = None
            mock_user1.role = "guardian"
            mock_user1.is_active = True
            mock_user1.email_verified = False
            mock_user1.last_login_at = None
            mock_user1.guardian_id = None
            mock_user1.created_at = now
            mock_user1.updated_at = now

            mock_user2 = MagicMock(spec=User)
            mock_user2.id = "user-2"
            mock_user2.email = "user2@example.com"
            mock_user2.full_name = "User 2"
            mock_user2.phone = None
            mock_user2.role = "authority"
            mock_user2.is_active = True
            mock_user2.email_verified = False
            mock_user2.last_login_at = None
            mock_user2.guardian_id = None
            mock_user2.created_at = now
            mock_user2.updated_at = now

            admin_service.user_repo.get_all = AsyncMock(
                return_value=[mock_user1, mock_user2]
            )

            users = await admin_service.list_users()
            assert len(users) == 2
            assert users[0].email == "user1@example.com"
            assert users[1].email == "user2@example.com"

        anyio.run(run_test)

    def test_admin_can_update_user(
        self, admin_service: AdminService, mock_guardian_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test admin can update a user's profile."""
        async def run_test():
            admin_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_guardian_user
            )
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            result = await admin_service.update_user(
                user_id="guardian-id",
                full_name="Updated Name",
                admin_id="admin-id",
            )

            assert result.full_name == "Updated Name"
            mock_session.commit.assert_called_once()

        anyio.run(run_test)

    def test_admin_can_activate_user(
        self, admin_service: AdminService, mock_guardian_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test admin can activate a user."""
        async def run_test():
            mock_guardian_user.is_active = False
            admin_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_guardian_user
            )
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            result = await admin_service.activate_user(
                user_id="guardian-id",
                admin_id="admin-id",
            )

            assert result.is_active is True

        anyio.run(run_test)

    def test_admin_can_deactivate_user(
        self, admin_service: AdminService, mock_guardian_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test admin can deactivate a user."""
        async def run_test():
            mock_guardian_user.is_active = True
            admin_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_guardian_user
            )
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            result = await admin_service.deactivate_user(
                user_id="guardian-id",
                admin_id="admin-id",
            )

            assert result.is_active is False

        anyio.run(run_test)

    def test_admin_can_change_role(
        self, admin_service: AdminService, mock_guardian_user: MagicMock,
        mock_session: AsyncMock
    ) -> None:
        """Test admin can change a user's role."""
        async def run_test():
            mock_guardian_user.role = "guardian"
            admin_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_guardian_user
            )
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            result = await admin_service.change_user_role(
                user_id="guardian-id",
                role="authority",
                admin_id="admin-id",
            )

            assert result.role == "authority"

        anyio.run(run_test)

    def test_admin_get_user_not_found(
        self, admin_service: AdminService
    ) -> None:
        """Test admin gets error when user not found."""
        async def run_test():
            admin_service.user_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(UserNotFound):
                await admin_service.get_user("nonexistent-id")

        anyio.run(run_test)

    def test_admin_change_role_invalid(
        self, admin_service: AdminService, mock_guardian_user: MagicMock
    ) -> None:
        """Test admin gets error with invalid role."""
        async def run_test():
            admin_service.user_repo.get_by_id = AsyncMock(
                return_value=mock_guardian_user
            )

            with pytest.raises(ValueError):
                await admin_service.change_user_role(
                    user_id="guardian-id",
                    role="invalid_role",
                    admin_id="admin-id",
                )

        anyio.run(run_test)