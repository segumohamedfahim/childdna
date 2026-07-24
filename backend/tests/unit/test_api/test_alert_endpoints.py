"""Integration Tests for Alert API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestAlertEndpoints:
    """Test cases for alert API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_alert_service(self) -> MagicMock:
        """Mock AlertService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.alert.AlertService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_list_alerts_success(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test successful alert listing"""
        # Arrange
        from app.schemas.alert import AlertListResponse, AlertResponse
        mock_alert_service.list_alerts = AsyncMock(
            return_value=AlertListResponse(
                alerts=[],
                total=0,
                skip=0,
                limit=20,
            )
        )

        # Act
        response = client.get("/api/v1/alerts")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["alerts"] == []
        assert data["total"] == 0

    def test_list_alerts_with_filters(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test alert listing with status and severity filters"""
        # Arrange
        from app.schemas.alert import AlertListResponse
        mock_alert_service.list_alerts = AsyncMock(
            return_value=AlertListResponse(
                alerts=[],
                total=0,
                skip=0,
                limit=20,
            )
        )

        # Act
        response = client.get(
            "/api/v1/alerts?status=open&severity=high"
        )

        # Assert
        assert response.status_code == 200
        mock_alert_service.list_alerts.assert_called_once_with(
            status="open", severity="high", skip=0, limit=20
        )

    def test_get_alert_success(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test successful alert retrieval"""
        # Arrange
        from app.schemas.alert import AlertResponse
        mock_alert_service.get_alert = AsyncMock(
            return_value=AlertResponse(
                id="alert-uuid-123",
                incident_id="incident-uuid-123",
                alert_type="match_found",
                severity="high",
                status="open",
                title="Test Alert",
                description="Test description",
                source="matching_engine",
            )
        )

        # Act
        response = client.get("/api/v1/alerts/alert-uuid-123")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "alert-uuid-123"
        assert data["status"] == "open"

    def test_get_alert_not_found(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test alert not found returns 404"""
        # Arrange
        from app.core.exceptions import AlertNotFound
        mock_alert_service.get_alert = AsyncMock(
            side_effect=AlertNotFound(alert_id="nonexistent-uuid")
        )

        # Act
        response = client.get("/api/v1/alerts/nonexistent-uuid")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "ALERT_NOT_FOUND" in str(data)

    def test_acknowledge_alert_success(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test successful alert acknowledgement"""
        # Arrange
        from app.schemas.alert import AlertResponse
        mock_alert_service.acknowledge_alert = AsyncMock(
            return_value=AlertResponse(
                id="alert-uuid-123",
                incident_id="incident-uuid-123",
                alert_type="match_found",
                severity="high",
                status="acknowledged",
                title="Test Alert",
                description="Test description",
                source="matching_engine",
                acknowledged_by="Officer Smith",
            )
        )

        # Act
        response = client.post(
            "/api/v1/alerts/alert-uuid-123/acknowledge",
            params={"acknowledged_by": "Officer Smith"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"

    def test_resolve_alert_success(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test successful alert resolution"""
        # Arrange
        from app.schemas.alert import AlertResponse
        mock_alert_service.resolve_alert = AsyncMock(
            return_value=AlertResponse(
                id="alert-uuid-123",
                incident_id="incident-uuid-123",
                alert_type="match_found",
                severity="high",
                status="resolved",
                title="Test Alert",
                description="Test description",
                source="matching_engine",
                resolved_by="Officer Smith",
            )
        )

        # Act
        response = client.post(
            "/api/v1/alerts/alert-uuid-123/resolve",
            params={"resolved_by": "Officer Smith"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_dismiss_alert_success(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test successful alert dismissal"""
        # Arrange
        from app.schemas.alert import AlertResponse
        mock_alert_service.dismiss_alert = AsyncMock(
            return_value=AlertResponse(
                id="alert-uuid-123",
                incident_id="incident-uuid-123",
                alert_type="match_found",
                severity="high",
                status="dismissed",
                title="Test Alert",
                description="Test description",
                source="matching_engine",
            )
        )

        # Act
        response = client.post(
            "/api/v1/alerts/alert-uuid-123/dismiss",
            params={"dismissed_by": "Officer Smith"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "dismissed"

    def test_get_alert_summary(
        self,
        client: TestClient,
        mock_alert_service: MagicMock,
    ) -> None:
        """Test alert summary endpoint"""
        # Arrange
        from app.schemas.alert import AlertSummaryResponse
        mock_alert_service.get_alert_summary = AsyncMock(
            return_value=AlertSummaryResponse(
                total_open=2,
                total_acknowledged=1,
                total_resolved=1,
                total_dismissed=0,
                by_severity={"high": 3, "low": 1},
                by_status={"open": 2, "acknowledged": 1, "resolved": 1},
            )
        )

        # Act
        response = client.get("/api/v1/alerts/summary")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_open"] == 2
        assert data["total_resolved"] == 1