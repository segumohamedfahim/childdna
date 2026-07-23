"""Integration Tests for Timeline API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestTimelineEndpoints:
    """Test cases for timeline API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_timeline_service(self) -> MagicMock:
        """Mock TimelineService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.timeline.TimelineService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_get_timeline_success(
        self,
        client: TestClient,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test getting timeline for an incident"""
        # Arrange
        from app.schemas.timeline_event import TimelineEventResponse
        from datetime import datetime, timezone
        mock_timeline_service.get_incident_timeline = AsyncMock(
            return_value=[
                TimelineEventResponse(
                    id="event-uuid",
                    child_id="child-uuid",
                    rescue_session_id="incident-uuid",
                    event_type="incident_created",
                    description="Rescue incident created",
                    created_by="system",
                    timestamp=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                )
            ]
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/timeline"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["event_type"] == "incident_created"

    def test_get_timeline_empty(
        self,
        client: TestClient,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test getting empty timeline"""
        # Arrange
        mock_timeline_service.get_incident_timeline = AsyncMock(
            return_value=[]
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/timeline"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_timeline_incident_not_found(
        self,
        client: TestClient,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test getting timeline for non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_timeline_service.get_incident_timeline = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/nonexistent/timeline"
        )

        # Assert
        assert response.status_code == 404