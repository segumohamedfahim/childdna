"""Integration Tests for Incident Intelligence API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestIntelligenceEndpoints:
    """Test cases for intelligence API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_intelligence_service(self) -> MagicMock:
        """Mock IncidentIntelligenceService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.intelligence.IncidentIntelligenceService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_analyze_success(
        self,
        client: TestClient,
        mock_intelligence_service: MagicMock,
    ) -> None:
        """Test successful analysis"""
        # Arrange
        from app.schemas.incident_analysis import AnalyzeResponse
        mock_intelligence_service.analyze = AsyncMock(
            return_value=AnalyzeResponse(
                incident_id="incident-uuid",
                raw_text="Small boy crying near fountain",
                analysis_engine="rule_engine_v1",
                overall_confidence=0.85,
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/analyze",
            json={"notes": "Small boy crying near fountain"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == "incident-uuid"
        assert data["analysis_engine"] == "rule_engine_v1"

    def test_analyze_incident_not_found(
        self,
        client: TestClient,
        mock_intelligence_service: MagicMock,
    ) -> None:
        """Test analysis for non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_intelligence_service.analyze = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/nonexistent/analyze",
            json={"notes": "test report"},
        )

        # Assert
        assert response.status_code == 404

    def test_analyze_short_text(
        self,
        client: TestClient,
    ) -> None:
        """Test analysis with text below minimum length"""
        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/analyze",
            json={"notes": "ab"},
        )

        # Assert
        assert response.status_code == 422

    def test_get_analysis_success(
        self,
        client: TestClient,
        mock_intelligence_service: MagicMock,
    ) -> None:
        """Test getting existing analysis"""
        # Arrange
        from app.schemas.incident_analysis import AnalyzeResponse
        mock_intelligence_service.get_analysis = AsyncMock(
            return_value=AnalyzeResponse(
                incident_id="incident-uuid",
                raw_text="test",
                analysis_engine="rule_engine_v1",
                overall_confidence=0.5,
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/analysis"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_engine"] == "rule_engine_v1"

    def test_get_analysis_not_found(
        self,
        client: TestClient,
        mock_intelligence_service: MagicMock,
    ) -> None:
        """Test getting analysis when none exists"""
        # Arrange
        from app.core.exceptions import AnalysisNotFound
        mock_intelligence_service.get_analysis = AsyncMock(
            side_effect=AnalysisNotFound(incident_id="incident-uuid")
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/analysis"
        )

        # Assert
        assert response.status_code == 404

    def test_get_analysis_incident_not_found(
        self,
        client: TestClient,
        mock_intelligence_service: MagicMock,
    ) -> None:
        """Test getting analysis for non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_intelligence_service.get_analysis = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/nonexistent/analysis"
        )

        # Assert
        assert response.status_code == 404