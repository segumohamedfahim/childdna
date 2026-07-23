"""Integration Tests for Rescue Incident API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestRescueEndpoints:
    """Test cases for rescue incident API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_rescue_service(self) -> MagicMock:
        """Mock RescueService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.rescue.RescueService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def _make_response(
        self, status: str = "pending"
    ) -> "RescueSessionResponse":
        """Helper to create a valid RescueSessionResponse"""
        from app.schemas.rescue_session import RescueSessionResponse
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        return RescueSessionResponse(
            id="incident-uuid",
            child_id="child-uuid",
            status=status,
            priority=1,
            rescuer_name="John Rescuer",
            rescuer_phone="+1234567890",
            created_at=now,
            updated_at=now,
        )

    def test_create_incident_success(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test successful incident creation"""
        # Arrange
        mock_rescue_service.create_incident = AsyncMock(
            return_value=self._make_response(status="pending")
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents",
            json={
                "child_id": "child-uuid",
                "priority": 1,
                "rescuer_name": "John Rescuer",
                "rescuer_phone": "+1234567890",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["child_id"] == "child-uuid"
        assert data["status"] == "pending"

    def test_create_incident_missing_child(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test incident creation with invalid child"""
        # Arrange
        from app.core.exceptions import ChildNotFound
        mock_rescue_service.create_incident = AsyncMock(
            side_effect=ChildNotFound(child_id="nonexistent")
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents",
            json={"child_id": "nonexistent"},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "CHILD_NOT_FOUND"

    def test_create_incident_duplicate(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test incident creation with duplicate active"""
        # Arrange
        from app.core.exceptions import ActiveRescueSessionExists
        mock_rescue_service.create_incident = AsyncMock(
            side_effect=ActiveRescueSessionExists(child_id="child-uuid")
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents",
            json={"child_id": "child-uuid"},
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "ACTIVE_RESCUE_SESSION_EXISTS"

    def test_list_incidents_success(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test listing incidents"""
        # Arrange
        mock_rescue_service.list_incidents = AsyncMock(
            return_value=[self._make_response(status="pending")]
        )

        # Act
        response = client.get("/api/v1/rescue/incidents")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_incident_success(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test getting incident by ID"""
        # Arrange
        mock_rescue_service.get_incident = AsyncMock(
            return_value=self._make_response(status="active")
        )

        # Act
        response = client.get("/api/v1/rescue/incidents/incident-uuid")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "incident-uuid"

    def test_get_incident_not_found(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test getting non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_rescue_service.get_incident = AsyncMock(
            side_effect=RescueSessionNotFound(incident_id="nonexistent")
        )

        # Act
        response = client.get("/api/v1/rescue/incidents/nonexistent")

        # Assert
        assert response.status_code == 404

    def test_update_incident_success(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test updating incident"""
        # Arrange
        mock_rescue_service.update_incident = AsyncMock(
            return_value=self._make_response(status="active")
        )

        # Act
        response = client.patch(
            "/api/v1/rescue/incidents/incident-uuid",
            json={"status": "active"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_update_incident_invalid_status(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test invalid status transition"""
        # Arrange
        from app.core.exceptions import InvalidSessionStatusTransition
        mock_rescue_service.update_incident = AsyncMock(
            side_effect=InvalidSessionStatusTransition(
                current_status="pending",
                requested_status="complete",
            )
        )

        # Act
        response = client.patch(
            "/api/v1/rescue/incidents/incident-uuid",
            json={"status": "complete"},
        )

        # Assert
        assert response.status_code == 400

    def test_get_child_incidents_success(
        self,
        client: TestClient,
        mock_rescue_service: MagicMock,
    ) -> None:
        """Test getting incidents for a child"""
        # Arrange
        from app.schemas.rescue_session import RescueSessionResponse
        mock_rescue_service.get_child_incidents = AsyncMock(
            return_value=[]
        )

        # Act
        response = client.get(
            "/api/v1/children/child-uuid/incidents"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == []