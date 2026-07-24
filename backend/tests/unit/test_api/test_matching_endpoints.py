"""Integration Tests for REUNITE Match API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestMatchingEndpoints:
    """Test cases for matching API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_matching_service(self) -> MagicMock:
        """Mock IncidentMatchingService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.matching.IncidentMatchingService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def test_match_incident_success(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test successful match finding"""
        # Arrange
        from app.schemas.incident_match import MatchListResponse
        mock_matching_service.find_matches = AsyncMock(
            return_value=MatchListResponse(
                incident_id="incident-uuid",
                matches=[],
                total_matches=0,
                algorithm_version="rule_engine_v1",
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/match",
            json={},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == "incident-uuid"
        assert data["total_matches"] == 0

    def test_match_incident_with_candidates(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test match finding with candidate filter"""
        # Arrange
        from app.schemas.incident_match import (
            MatchListResponse,
            MatchResponse,
        )
        mock_matching_service.find_matches = AsyncMock(
            return_value=MatchListResponse(
                incident_id="incident-uuid",
                matches=[
                    MatchResponse(
                        matched_incident_id="candidate-uuid",
                        similarity_score=0.85,
                        match_category="high",
                        recommendation="likely_match",
                        score_breakdown={"total_score": 0.85},
                        algorithm_version="rule_engine_v1",
                    )
                ],
                total_matches=1,
                algorithm_version="rule_engine_v1",
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/incident-uuid/match",
            json={"candidate_incident_ids": ["candidate-uuid"]},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] == 1
        assert data["matches"][0]["matched_incident_id"] == "candidate-uuid"
        assert data["matches"][0]["similarity_score"] == 0.85
        assert data["matches"][0]["match_category"] == "high"

    def test_match_incident_incident_not_found(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test match finding for non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_matching_service.find_matches = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.post(
            "/api/v1/rescue/incidents/nonexistent/match",
            json={},
        )

        # Assert
        assert response.status_code == 404

    def test_get_incident_matches_success(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test getting stored matches"""
        # Arrange
        from app.schemas.incident_match import (
            MatchListResponse,
            MatchResponse,
        )
        mock_matching_service.get_matches = AsyncMock(
            return_value=MatchListResponse(
                incident_id="incident-uuid",
                matches=[
                    MatchResponse(
                        matched_incident_id="matched-uuid",
                        similarity_score=0.85,
                        match_category="high",
                        recommendation="likely_match",
                        algorithm_version="rule_engine_v1",
                    )
                ],
                total_matches=1,
                algorithm_version="rule_engine_v1",
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/matches"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == "incident-uuid"
        assert data["total_matches"] == 1
        assert data["matches"][0]["match_category"] == "high"

    def test_get_incident_matches_empty(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test getting stored matches when none exist"""
        # Arrange
        from app.schemas.incident_match import MatchListResponse
        mock_matching_service.get_matches = AsyncMock(
            return_value=MatchListResponse(
                incident_id="incident-uuid",
                matches=[],
                total_matches=0,
                algorithm_version="rule_engine_v1",
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/incident-uuid/matches"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_matches"] == 0

    def test_get_incident_matches_not_found(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test getting matches for non-existent incident"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_matching_service.get_matches = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent"
            )
        )

        # Act
        response = client.get(
            "/api/v1/rescue/incidents/nonexistent/matches"
        )

        # Assert
        assert response.status_code == 404

    def test_compare_analyses_success(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test comparing two analyses"""
        # Arrange
        from app.schemas.incident_match import CompareResponse
        mock_matching_service.compare = AsyncMock(
            return_value=CompareResponse(
                incident_id_a="incident-a-uuid",
                incident_id_b="incident-b-uuid",
                similarity_score=0.55,
                match_category="medium",
                recommendation="possible_match",
                score_breakdown={"total_score": 0.55},
                algorithm_version="rule_engine_v1",
            )
        )

        # Act
        response = client.post(
            "/api/v1/reunite/compare",
            json={
                "incident_id_a": "incident-a-uuid",
                "incident_id_b": "incident-b-uuid",
            },
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id_a"] == "incident-a-uuid"
        assert data["incident_id_b"] == "incident-b-uuid"
        assert data["similarity_score"] == 0.55
        assert data["match_category"] == "medium"

    def test_compare_analyses_not_found(
        self,
        client: TestClient,
        mock_matching_service: MagicMock,
    ) -> None:
        """Test comparing two analyses when one not found"""
        # Arrange
        from app.core.exceptions import RescueSessionNotFound
        mock_matching_service.compare = AsyncMock(
            side_effect=RescueSessionNotFound(
                incident_id="nonexistent-a"
            )
        )

        # Act
        response = client.post(
            "/api/v1/reunite/compare",
            json={
                "incident_id_a": "nonexistent-a",
                "incident_id_b": "incident-b-uuid",
            },
        )

        # Assert
        assert response.status_code == 404

    def test_compare_analyses_validation_error(
        self,
        client: TestClient,
    ) -> None:
        """Test comparing with missing request body"""
        # Act
        response = client.post(
            "/api/v1/reunite/compare",
            json={},
        )

        # Assert
        assert response.status_code == 422