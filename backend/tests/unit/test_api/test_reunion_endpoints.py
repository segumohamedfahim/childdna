"""Integration Tests for Reunion API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestReunionEndpoints:
    """Test cases for reunion API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_reunion_service(self) -> MagicMock:
        """Mock ReunionService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.reunion.ReunionService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_record_reunion_success(
        self,
        client: TestClient,
        mock_reunion_service: MagicMock,
    ) -> None:
        """Test successful reunion recording"""
        # Arrange
        from app.schemas.reunion_record import ReunionRecordResponse
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        mock_reunion_service.record_reunion = AsyncMock(
            return_value=ReunionRecordResponse(
                id="reunion-uuid",
                child_id="child-uuid",
                rescuer_name="John Rescuer",
                guardian_name="Jane Doe",
                reunion_time=now,
                verification_method="guardian_id_card",
                created_at=now,
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/reunion",
            json={
                "child_id": "child-uuid",
                "rescuer_name": "John Rescuer",
                "guardian_name": "Jane Doe",
                "reunion_time": "2026-07-23T14:30:00Z",
                "verification_method": "guardian_id_card",
            },
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["guardian_name"] == "Jane Doe"

    def test_record_reunion_incident_not_found(
        self,
        client: TestClient,
        mock_reunion_service: MagicMock,
    ) -> None:
        """Test reunion with non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_reunion_service.record_reunion = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/nonexistent/reunion",
            json={
                "child_id": "child-uuid",
                "rescuer_name": "John Rescuer",
                "guardian_name": "Jane Doe",
                "reunion_time": "2026-07-23T14:30:00Z",
                "verification_method": "guardian_id_card",
            },
        )

        # Assert
        assert response.status_code == 404

    def test_record_reunion_incident_not_active(
        self,
        client: TestClient,
        mock_reunion_service: MagicMock,
    ) -> None:
        """Test reunion with non-active incident"""
        # Arrange
        from app.core.exceptions import InvalidSessionStatusTransition
        mock_reunion_service.record_reunion = AsyncMock(
            side_effect=InvalidSessionStatusTransition(
                current_status="pending",
                requested_status="complete",
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/reunion",
            json={
                "child_id": "child-uuid",
                "rescuer_name": "John Rescuer",
                "guardian_name": "Jane Doe",
                "reunion_time": "2026-07-23T14:30:00Z",
                "verification_method": "guardian_id_card",
            },
        )

        # Assert
        assert response.status_code == 400

    def test_get_child_reunions_success(
        self,
        client: TestClient,
        mock_reunion_service: MagicMock,
    ) -> None:
        """Test getting reunions for a child"""
        # Arrange
        mock_reunion_service.get_child_reunions = AsyncMock(
            return_value=[]
        )

        # Act
        response = client.get(
            "/api/v1/children/child-uuid/reunions"
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == []