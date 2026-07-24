"""Unit Tests for Incident Intelligence Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import anyio
from app.services.incident_intelligence_service import IncidentIntelligenceService
from app.schemas.incident_analysis import AnalyzeRequest, AnalyzeResponse
from app.core.exceptions import RescueSessionNotFound, AnalysisNotFound


class TestIncidentIntelligenceService:
    """Test cases for IncidentIntelligenceService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def intelligence_service(
        self, mock_session: AsyncMock,
    ) -> IncidentIntelligenceService:
        """Create IncidentIntelligenceService with mock session"""
        return IncidentIntelligenceService(mock_session)

    @pytest.fixture
    def mock_rescue_repo(
        self, intelligence_service: IncidentIntelligenceService,
    ) -> MagicMock:
        """Mock rescue session repository"""
        return intelligence_service.rescue_repo

    @pytest.fixture
    def mock_analysis_repo(
        self, intelligence_service: IncidentIntelligenceService,
    ) -> MagicMock:
        """Mock analysis repository"""
        return intelligence_service.analysis_repo

    def test_analyze_success(
        self,
        intelligence_service: IncidentIntelligenceService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test successful analysis"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            request = AnalyzeRequest(notes="Small boy crying near fountain")
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            mock_analysis = MagicMock()
            mock_analysis.id = "analysis-uuid"
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
            mock_analysis_repo.create_from_dict = AsyncMock(
                return_value=mock_analysis
            )

            # Act
            result = await intelligence_service.analyze(
                incident_id, request
            )

            # Assert
            assert isinstance(result, AnalyzeResponse)
            mock_rescue_repo.get_by_id.assert_called_once_with(
                incident_id
            )
            mock_analysis_repo.create_from_dict.assert_called_once()

        anyio.run(run_test)

    def test_analyze_incident_not_found(
        self,
        intelligence_service: IncidentIntelligenceService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test analysis with non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            request = AnalyzeRequest(notes="test report")
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await intelligence_service.analyze(incident_id, request)

        anyio.run(run_test)

    def test_get_analysis_success(
        self,
        intelligence_service: IncidentIntelligenceService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test getting existing analysis"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            mock_analysis = MagicMock()
            mock_analysis.id = "analysis-uuid"
            mock_analysis.incident_id = incident_id
            mock_analysis.raw_text = "test"
            mock_analysis.analysis_engine = "rule_engine_v1"
            mock_analysis.gender = None
            mock_analysis.gender_confidence = 0.0
            mock_analysis.estimated_age_min = None
            mock_analysis.estimated_age_max = None
            mock_analysis.age_confidence = 0.0
            mock_analysis.emotion = None
            mock_analysis.emotion_confidence = 0.0
            mock_analysis.clothing = []
            mock_analysis.clothing_confidence = 0.0
            mock_analysis.location = None
            mock_analysis.location_confidence = 0.0
            mock_analysis.distinguishing_features = []
            mock_analysis.features_confidence = 0.0
            mock_analysis.overall_confidence = 0.5
            mock_analysis.created_at = None
            mock_analysis_repo.get_by_incident = AsyncMock(
                return_value=mock_analysis
            )

            # Act
            result = await intelligence_service.get_analysis(
                incident_id
            )

            # Assert
            assert isinstance(result, AnalyzeResponse)
            mock_analysis_repo.get_by_incident.assert_called_once_with(
                incident_id
            )

        anyio.run(run_test)

    def test_get_analysis_not_found(
        self,
        intelligence_service: IncidentIntelligenceService,
        mock_rescue_repo: MagicMock,
        mock_analysis_repo: MagicMock,
    ) -> None:
        """Test getting analysis when none exists"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
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
                await intelligence_service.get_analysis(incident_id)

        anyio.run(run_test)

    def test_get_analysis_incident_not_found(
        self,
        intelligence_service: IncidentIntelligenceService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting analysis for non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await intelligence_service.get_analysis(incident_id)

        anyio.run(run_test)