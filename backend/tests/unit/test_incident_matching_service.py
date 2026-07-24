"""Unit Tests for Incident Matching Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.incident_matching_service import IncidentMatchingService
from app.schemas.incident_match import (
    MatchRequest,
    MatchListResponse,
    MatchResponse,
    CompareRequest,
    CompareResponse,
)
from app.core.exceptions import RescueSessionNotFound, AnalysisNotFound


class TestIncidentMatchingService:
    """Test cases for IncidentMatchingService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def matching_service(
        self, mock_session: AsyncMock,
    ) -> IncidentMatchingService:
        """Create IncidentMatchingService with mock session"""
        return IncidentMatchingService(mock_session)

    @pytest.fixture
    def mock_rescue_repo(
        self, matching_service: IncidentMatchingService,
    ) -> MagicMock:
        """Mock rescue session repository"""
        return matching_service.rescue_repo

    @pytest.fixture
    def mock_analysis_repo(
        self, matching_service: IncidentMatchingService,
    ) -> MagicMock:
        """Mock analysis repository"""
        return matching_service.analysis_repo

    @pytest.fixture
    def mock_match_repo(
        self, matching_service: IncidentMatchingService,
    ) -> MagicMock:
        """Mock match repository"""
        return matching_service.match_repo

    def test_find_matches_success(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
        mock_match_repo: MagicMock,
    ) -> None:
        """Test successful match finding"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            request = MatchRequest()

            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )

            mock_analysis = MagicMock()
            mock_analysis.incident_id = incident_id
            mock_analysis.raw_text = "Small boy crying near fountain"
            mock_analysis.analysis_engine = "rule_engine_v1"
            mock_analysis.gender = "male"
            mock_analysis.gender_confidence = 0.95
            mock_analysis.estimated_age_min = None
            mock_analysis.estimated_age_max = None
            mock_analysis.age_confidence = 0.0
            mock_analysis.emotion = "distressed"
            mock_analysis.emotion_confidence = 0.92
            mock_analysis.clothing = ["blue shirt"]
            mock_analysis.clothing_confidence = 0.85
            mock_analysis.location = "fountain"
            mock_analysis.location_confidence = 0.85
            mock_analysis.distinguishing_features = []
            mock_analysis.features_confidence = 0.0
            mock_analysis.overall_confidence = 0.85
            mock_analysis.created_at = None
            mock_analysis_repo.get_by_incident = AsyncMock(
                return_value=mock_analysis
            )

            # Mock get_all to return no candidates
            mock_analysis_repo.get_all = AsyncMock(return_value=[])

            # Act
            result = await matching_service.find_matches(
                incident_id, request
            )

            # Assert
            assert isinstance(result, MatchListResponse)
            assert result.incident_id == incident_id
            assert result.total_matches == 0
            mock_rescue_repo.get_by_id.assert_called_once_with(
                incident_id
            )
            mock_analysis_repo.get_by_incident.assert_called_once_with(
                incident_id
            )

        anyio.run(run_test)

    def test_find_matches_incident_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test match finding with non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            request = MatchRequest()
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await matching_service.find_matches(
                    incident_id, request
                )

        anyio.run(run_test)

    def test_find_matches_analysis_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test match finding when source has no analysis"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            request = MatchRequest()

            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            mock_analysis_repo.get_by_incident = AsyncMock(
                return_value=None
            )

            # Act & Assert
            with pytest.raises(AnalysisNotFound):
                await matching_service.find_matches(
                    incident_id, request
                )

        anyio.run(run_test)

    def test_get_matches_success(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_match_repo: MagicMock,
    ) -> None:
        """Test getting stored matches"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"

            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )

            mock_match = MagicMock()
            mock_match.matched_incident_id = "matched-uuid"
            mock_match.similarity_score = 0.85
            mock_match.match_category = "high"
            mock_match.recommendation = "likely_match"
            mock_match.score_breakdown = {"total_score": 0.85}
            mock_match.algorithm_version = "rule_engine_v1"
            mock_match.created_at = None
            mock_match_repo.get_top_matches = AsyncMock(
                return_value=[mock_match]
            )

            # Act
            result = await matching_service.get_matches(incident_id)

            # Assert
            assert isinstance(result, MatchListResponse)
            assert result.incident_id == incident_id
            assert result.total_matches == 1
            assert result.matches[0].matched_incident_id == "matched-uuid"
            assert result.matches[0].similarity_score == 0.85
            assert result.matches[0].match_category == "high"
            assert result.matches[0].recommendation == "likely_match"

        anyio.run(run_test)

    def test_get_matches_incident_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting matches for non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await matching_service.get_matches(incident_id)

        anyio.run(run_test)

    def test_compare_success(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test comparing two analyses"""
        async def run_test():
            # Arrange
            request = CompareRequest(
                incident_id_a="incident-a-uuid",
                incident_id_b="incident-b-uuid",
            )

            mock_incident_a = MagicMock()
            mock_incident_a.id = "incident-a-uuid"
            mock_incident_b = MagicMock()
            mock_incident_b.id = "incident-b-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(
                side_effect=[mock_incident_a, mock_incident_b]
            )

            mock_analysis_a = MagicMock()
            mock_analysis_a.incident_id = "incident-a-uuid"
            mock_analysis_a.raw_text = "Small boy crying near fountain"
            mock_analysis_a.analysis_engine = "rule_engine_v1"
            mock_analysis_a.gender = "male"
            mock_analysis_a.gender_confidence = 0.95
            mock_analysis_a.estimated_age_min = None
            mock_analysis_a.estimated_age_max = None
            mock_analysis_a.age_confidence = 0.0
            mock_analysis_a.emotion = "distressed"
            mock_analysis_a.emotion_confidence = 0.92
            mock_analysis_a.clothing = ["blue shirt"]
            mock_analysis_a.clothing_confidence = 0.85
            mock_analysis_a.location = "fountain"
            mock_analysis_a.location_confidence = 0.85
            mock_analysis_a.distinguishing_features = []
            mock_analysis_a.features_confidence = 0.0
            mock_analysis_a.overall_confidence = 0.85
            mock_analysis_a.created_at = None

            mock_analysis_b = MagicMock()
            mock_analysis_b.incident_id = "incident-b-uuid"
            mock_analysis_b.raw_text = "Small girl near fountain"
            mock_analysis_b.analysis_engine = "rule_engine_v1"
            mock_analysis_b.gender = "female"
            mock_analysis_b.gender_confidence = 0.90
            mock_analysis_b.estimated_age_min = None
            mock_analysis_b.estimated_age_max = None
            mock_analysis_b.age_confidence = 0.0
            mock_analysis_b.emotion = None
            mock_analysis_b.emotion_confidence = 0.0
            mock_analysis_b.clothing = []
            mock_analysis_b.clothing_confidence = 0.0
            mock_analysis_b.location = "fountain"
            mock_analysis_b.location_confidence = 0.85
            mock_analysis_b.distinguishing_features = []
            mock_analysis_b.features_confidence = 0.0
            mock_analysis_b.overall_confidence = 0.5
            mock_analysis_b.created_at = None

            mock_analysis_repo.get_by_incident = AsyncMock(
                side_effect=[mock_analysis_a, mock_analysis_b]
            )

            # Act
            result = await matching_service.compare(request)

            # Assert
            assert isinstance(result, CompareResponse)
            assert result.incident_id_a == "incident-a-uuid"
            assert result.incident_id_b == "incident-b-uuid"
            assert result.similarity_score >= 0.0
            assert result.match_category in [
                "no_match", "low", "medium", "high", "very_high", "identical"
            ]

        anyio.run(run_test)

    def test_compare_incident_a_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test compare with first incident not found"""
        async def run_test():
            # Arrange
            request = CompareRequest(
                incident_id_a="nonexistent-a",
                incident_id_b="incident-b-uuid",
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await matching_service.compare(request)

        anyio.run(run_test)

    def test_compare_analysis_a_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test compare with first analysis not found"""
        async def run_test():
            # Arrange
            request = CompareRequest(
                incident_id_a="incident-a-uuid",
                incident_id_b="incident-b-uuid",
            )

            mock_incident_a = MagicMock()
            mock_incident_a.id = "incident-a-uuid"
            mock_incident_b = MagicMock()
            mock_incident_b.id = "incident-b-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(
                side_effect=[mock_incident_a, mock_incident_b]
            )
            mock_analysis_repo.get_by_incident = AsyncMock(
                return_value=None
            )

            # Act & Assert
            with pytest.raises(AnalysisNotFound):
                await matching_service.compare(request)

        anyio.run(run_test)

    def test_delete_matches_success(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
        mock_match_repo: MagicMock,
    ) -> None:
        """Test deleting matches"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"

            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            mock_match_repo.delete_matches = AsyncMock()

            # Act
            await matching_service.delete_matches(incident_id)

            # Assert
            mock_match_repo.delete_matches.assert_called_once_with(
                incident_id
            )

        anyio.run(run_test)

    def test_delete_matches_incident_not_found(
        self,
        matching_service: IncidentMatchingService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test deleting matches for non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await matching_service.delete_matches(incident_id)

        anyio.run(run_test)