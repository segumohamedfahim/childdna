"""Unit Tests for Notification Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
)
from app.core.exceptions import GuardianNotFound, ChildNotFound


class TestNotificationService:
    """Test cases for NotificationService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def notification_service(
        self, mock_session: AsyncMock,
    ) -> NotificationService:
        """Create NotificationService with mock session"""
        return NotificationService(mock_session)

    @pytest.fixture
    def mock_notification_repo(
        self, notification_service: NotificationService,
    ) -> MagicMock:
        """Mock notification repository"""
        return notification_service.notification_repo

    @pytest.fixture
    def mock_guardian_repo(
        self, notification_service: NotificationService,
    ) -> MagicMock:
        """Mock guardian repository"""
        return notification_service.guardian_repo

    @pytest.fixture
    def mock_child_repo(
        self, notification_service: NotificationService,
    ) -> MagicMock:
        """Mock child repository"""
        return notification_service.child_repo

    def _make_notification_mock(self, **kwargs) -> MagicMock:
        """Helper to create notification mock with proper string values"""
        n = MagicMock()
        n.id = kwargs.get("id", "notif-uuid-123")
        n.guardian_id = kwargs.get("guardian_id", "guardian-uuid-123")
        n.child_id = kwargs.get("child_id", "child-uuid-123")
        n.incident_id = kwargs.get("incident_id", "incident-uuid-123")
        n.notification_type = kwargs.get("notification_type", "incident_created")
        n.channel = kwargs.get("channel", "in_app")
        n.status = kwargs.get("status", "pending")
        n.title = kwargs.get("title", "Rescue Started")
        n.message = kwargs.get("message", "A rescue incident has been created.")
        n.extra_data = kwargs.get("extra_data", None)
        n.read_at = kwargs.get("read_at", None)
        n.sent_at = kwargs.get("sent_at", None)
        n.delivered_at = kwargs.get("delivered_at", None)
        n.created_at = kwargs.get("created_at", None)
        return n

    def test_dispatch_success(
        self,
        notification_service: NotificationService,
        mock_guardian_repo: MagicMock,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful notification dispatch"""
        async def run_test():
            mock_guardian_repo.get_by_id = AsyncMock(
                return_value=MagicMock(id="guardian-uuid-123")
            )

            # Make refresh set the id on the notification
            async def _refresh(entity):
                entity.id = "notif-uuid-123"
            mock_session.refresh = AsyncMock(side_effect=_refresh)

            result = await notification_service.dispatch(
                guardian_id="guardian-uuid-123",
                child_id="child-uuid-123",
                incident_id="incident-uuid-123",
                notification_type="incident_created",
                title="Rescue Started",
                message="A rescue incident has been created.",
            )

            assert isinstance(result, NotificationResponse)
            assert result.guardian_id == "guardian-uuid-123"
            assert result.notification_type == "incident_created"
            mock_guardian_repo.get_by_id.assert_awaited_once_with(
                "guardian-uuid-123"
            )
            mock_session.add.assert_called_once()
            mock_session.commit.assert_awaited_once()

        anyio.run(run_test)

    def test_dispatch_guardian_not_found(
        self,
        notification_service: NotificationService,
        mock_guardian_repo: MagicMock,
    ) -> None:
        """Test dispatch with nonexistent guardian raises error"""
        async def run_test():
            mock_guardian_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(GuardianNotFound):
                await notification_service.dispatch(
                    guardian_id="nonexistent-uuid",
                    notification_type="status_changed",
                    title="Test",
                    message="Test message",
                )

        anyio.run(run_test)

    def test_get_notifications(
        self,
        notification_service: NotificationService,
        mock_notification_repo: MagicMock,
    ) -> None:
        """Test listing notifications for a guardian"""
        async def run_test():
            sample = self._make_notification_mock()
            mock_notification_repo.get_by_guardian = AsyncMock(
                return_value=[sample]
            )

            result = await notification_service.get_notifications(
                "guardian-uuid-123"
            )

            assert isinstance(result, NotificationListResponse)
            assert len(result.notifications) == 1
            assert result.notifications[0].id == "notif-uuid-123"
            mock_notification_repo.get_by_guardian.assert_awaited_once_with(
                "guardian-uuid-123", 0, 20
            )

        anyio.run(run_test)

    def test_get_unread_count(
        self,
        notification_service: NotificationService,
        mock_notification_repo: MagicMock,
    ) -> None:
        """Test getting unread notification count"""
        async def run_test():
            mock_notification_repo.get_unread_count = AsyncMock(
                return_value=5
            )

            result = await notification_service.get_unread_count(
                "guardian-uuid-123"
            )

            assert result == 5
            mock_notification_repo.get_unread_count.assert_awaited_once_with(
                "guardian-uuid-123"
            )

        anyio.run(run_test)

    def test_mark_as_read(
        self,
        notification_service: NotificationService,
        mock_notification_repo: MagicMock,
    ) -> None:
        """Test marking a notification as read"""
        async def run_test():
            read_notification = self._make_notification_mock(
                read_at=MagicMock()
            )
            mock_notification_repo.mark_as_read = AsyncMock(
                return_value=read_notification
            )

            result = await notification_service.mark_as_read("notif-uuid-123")

            assert isinstance(result, NotificationResponse)
            assert result.id == "notif-uuid-123"
            mock_notification_repo.mark_as_read.assert_awaited_once_with(
                "notif-uuid-123"
            )

        anyio.run(run_test)

    def test_mark_all_as_read(
        self,
        notification_service: NotificationService,
        mock_notification_repo: MagicMock,
    ) -> None:
        """Test marking all notifications as read"""
        async def run_test():
            mock_notification_repo.mark_all_as_read = AsyncMock(
                return_value=3
            )

            result = await notification_service.mark_all_as_read(
                "guardian-uuid-123"
            )

            assert result == 3
            mock_notification_repo.mark_all_as_read.assert_awaited_once_with(
                "guardian-uuid-123"
            )

        anyio.run(run_test)

    def test_get_summary(
        self,
        notification_service: NotificationService,
        mock_notification_repo: MagicMock,
    ) -> None:
        """Test getting notification summary"""
        async def run_test():
            mock_notification_repo.get_unread_count = AsyncMock(
                return_value=2
            )
            mock_notification_repo.get_summary = AsyncMock(
                return_value={
                    "by_type": {"incident_created": 3, "status_changed": 1},
                    "by_status": {"pending": 2, "sent": 2},
                }
            )

            result = await notification_service.get_summary(
                "guardian-uuid-123"
            )

            assert isinstance(result, NotificationSummaryResponse)
            assert result.total_unread == 2
            assert result.total_sent == 4
            assert result.by_type == {
                "incident_created": 3, "status_changed": 1
            }

        anyio.run(run_test)

    def test_resolve_guardian_success(
        self,
        notification_service: NotificationService,
        mock_child_repo: MagicMock,
    ) -> None:
        """Test resolving guardian from child ID"""
        async def run_test():
            child = MagicMock()
            child.guardian_id = "guardian-uuid-123"
            mock_child_repo.get_by_id = AsyncMock(return_value=child)

            result = await notification_service.resolve_guardian(
                "child-uuid-123"
            )

            assert result == "guardian-uuid-123"
            mock_child_repo.get_by_id.assert_awaited_once_with(
                "child-uuid-123"
            )

        anyio.run(run_test)

    def test_resolve_guardian_child_not_found(
        self,
        notification_service: NotificationService,
        mock_child_repo: MagicMock,
    ) -> None:
        """Test resolving guardian from nonexistent child"""
        async def run_test():
            mock_child_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(ChildNotFound):
                await notification_service.resolve_guardian(
                    "nonexistent-uuid"
                )

        anyio.run(run_test)

    def test_build_message_incident_created(self) -> None:
        """Test building incident_created notification message"""
        title, message = NotificationService.build_message(
            "incident_created",
            {"child_name": "Alice"},
        )
        assert "Alice" in title
        assert "Rescue" in title
        assert "responding" in message

    def test_build_message_reunion_completed(self) -> None:
        """Test building reunion_completed notification message"""
        title, message = NotificationService.build_message(
            "reunion_completed",
            {"child_name": "Bob", "guardian_name": "Carol"},
        )
        assert "Bob" in title
        assert "Carol" in message
        assert "Reunited" in title

    def test_build_message_unknown_type(self) -> None:
        """Test building message for unknown notification type"""
        title, message = NotificationService.build_message(
            "unknown_type",
            {"child_name": "Dave"},
        )
        assert "Notification" in title
        assert "Dave" in message