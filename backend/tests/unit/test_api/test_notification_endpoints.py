"""Integration Tests for Notification API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestNotificationEndpoints:
    """Test cases for notification API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_notification_service(self) -> MagicMock:
        """Mock NotificationService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.notification.NotificationService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_list_notifications_success(
        self,
        client: TestClient,
        mock_notification_service: MagicMock,
    ) -> None:
        """Test successful notification listing"""
        # Arrange
        from app.schemas.notification import (
            NotificationListResponse,
        )
        mock_notification_service.get_notifications = AsyncMock(
            return_value=NotificationListResponse(
                notifications=[],
                total=0,
                skip=0,
                limit=20,
            )
        )

        # Act
        response = client.get(
            "/api/v1/guardians/guardian-uuid-123/notifications"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["notifications"] == []
        assert data["total"] == 0

    def test_get_unread_count(
        self,
        client: TestClient,
        mock_notification_service: MagicMock,
    ) -> None:
        """Test unread notification count endpoint"""
        # Arrange
        mock_notification_service.get_unread_count = AsyncMock(
            return_value=5
        )

        # Act
        response = client.get(
            "/api/v1/guardians/guardian-uuid-123/notifications/unread-count"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["guardian_id"] == "guardian-uuid-123"
        assert data["unread_count"] == 5

    def test_mark_as_read_success(
        self,
        client: TestClient,
        mock_notification_service: MagicMock,
    ) -> None:
        """Test marking notification as read"""
        # Arrange
        from app.schemas.notification import NotificationResponse
        from datetime import datetime, timezone
        mock_notification_service.mark_as_read = AsyncMock(
            return_value=NotificationResponse(
                id="notif-uuid-123",
                guardian_id="guardian-uuid-123",
                notification_type="status_changed",
                channel="in_app",
                status="sent",
                title="Status Update",
                message="Status has changed",
                read_at=datetime.now(timezone.utc),
            )
        )

        # Act
        response = client.post(
            "/api/v1/notifications/notif-uuid-123/read"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "notif-uuid-123"
        assert data["read_at"] is not None

    def test_mark_all_as_read(
        self,
        client: TestClient,
        mock_notification_service: MagicMock,
    ) -> None:
        """Test marking all notifications as read"""
        # Arrange
        mock_notification_service.mark_all_as_read = AsyncMock(
            return_value=3
        )

        # Act
        response = client.post(
            "/api/v1/guardians/guardian-uuid-123/notifications/read-all"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["guardian_id"] == "guardian-uuid-123"
        assert data["updated"] == 3

    def test_get_notification_summary(
        self,
        client: TestClient,
        mock_notification_service: MagicMock,
    ) -> None:
        """Test notification summary endpoint"""
        # Arrange
        from app.schemas.notification import (
            NotificationSummaryResponse,
        )
        mock_notification_service.get_summary = AsyncMock(
            return_value=NotificationSummaryResponse(
                total_unread=2,
                total_sent=4,
                by_type={"incident_created": 3, "status_changed": 1},
                by_status={"pending": 2, "sent": 2},
            )
        )

        # Act
        response = client.get(
            "/api/v1/guardians/guardian-uuid-123/notifications/summary"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_unread"] == 2
        assert data["total_sent"] == 4