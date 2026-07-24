"""Unit Tests for Prediction Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
import anyio
from app.services.prediction_service import PredictionService
from app.models.child import Child
from app.models.guardian import Guardian
from app.models.rescue_session import RescueSession
from app.models.reunion_record import ReunionRecord
from app.models.incident_analysis import IncidentAnalysis
from app.models.incident_match import IncidentMatch
from app.models.enums import SessionStatus, ChildStatus


class TestPredictionService:
    """Test cases for PredictionService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def prediction_service(self, mock_session: AsyncMock) -> PredictionService:
        return PredictionService(mock_session)

    def test_predict_reunion_probability(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test reunion probability prediction."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.guardian_id = "guardian-1"
            mock_child.status = ChildStatus.ACTIVE

            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.is_active = True

            prediction_service.child_repo.get_by_id = AsyncMock(return_value=mock_child)
            prediction_service.guardian_repo.get_by_id = AsyncMock(return_value=mock_guardian)
            prediction_service.rescue_repo.get_by_child = AsyncMock(return_value=[])
            prediction_service.reunion_repo.get_by_child = AsyncMock(return_value=[])

            result = await prediction_service.predict_reunion_probability("child-1")

            assert result.child_id == "child-1"
            assert 0.0 <= result.reunion_probability <= 1.0
            assert len(result.factors) > 0
            assert result.confidence in ("low", "medium", "high")

        anyio.run(run_test)

    def test_predict_rescue_success(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test rescue success prediction."""
        async def run_test():
            mock_rescue = MagicMock(spec=RescueSession)
            mock_rescue.id = "rescue-1"
            mock_rescue.status = SessionStatus.ACTIVE
            mock_rescue.priority = 1
            mock_rescue.rescuer_name = "John Doe"
            mock_rescue.latitude = 40.7128
            mock_rescue.longitude = -74.0060
            mock_rescue.started_at = datetime.now(timezone.utc)
            mock_rescue.ended_at = None

            prediction_service.rescue_repo.get_by_id = AsyncMock(return_value=mock_rescue)

            result = await prediction_service.predict_rescue_success("rescue-1")

            assert result.rescue_session_id == "rescue-1"
            assert 0.0 <= result.success_probability <= 1.0
            assert len(result.factors) > 0

        anyio.run(run_test)

    def test_predict_incident_risk(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test incident risk prediction."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.guardian_id = "guardian-1"
            mock_child.status = ChildStatus.ACTIVE

            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.is_active = True

            prediction_service.child_repo.get_by_id = AsyncMock(return_value=mock_child)
            prediction_service.guardian_repo.get_by_id = AsyncMock(return_value=mock_guardian)
            prediction_service.rescue_repo.get_by_child = AsyncMock(return_value=[])
            prediction_service.analysis_repo.get_all = AsyncMock(return_value=[])

            result = await prediction_service.predict_incident_risk("child-1")

            assert result.child_id == "child-1"
            assert 0.0 <= result.risk_score <= 1.0
            assert result.risk_level in ("low", "medium", "high", "unknown")

        anyio.run(run_test)

    def test_predict_alert_probability(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test alert probability prediction."""
        async def run_test():
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_analysis.id = "analysis-1"
            mock_analysis.overall_confidence = 0.85
            mock_analysis.gender = "male"
            mock_analysis.estimated_age_min = 5
            mock_analysis.emotion = "distressed"
            mock_analysis.clothing = {"shirt": "red"}
            mock_analysis.location = "park"
            mock_analysis.distinguishing_features = {"scar": "left cheek"}

            prediction_service.analysis_repo.get_by_id = AsyncMock(return_value=mock_analysis)

            result = await prediction_service.predict_alert_probability("analysis-1")

            assert result.incident_analysis_id == "analysis-1"
            assert 0.0 <= result.alert_probability <= 1.0

        anyio.run(run_test)

    def test_generate_priority_score(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test priority score generation."""
        async def run_test():
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_analysis.id = "analysis-1"
            mock_analysis.overall_confidence = 0.85
            mock_analysis.estimated_age_min = 4
            mock_analysis.emotion = "distressed"
            mock_analysis.clothing = {"shirt": "blue"}
            mock_analysis.distinguishing_features = {"backpack": "red"}

            prediction_service.analysis_repo.get_by_id = AsyncMock(return_value=mock_analysis)

            result = await prediction_service.generate_priority_score("analysis-1")

            assert result.incident_analysis_id == "analysis-1"
            assert 0.0 <= result.priority_score <= 1.0
            assert result.priority_level in ("low", "medium", "high", "critical")

        anyio.run(run_test)

    def test_generate_ai_summary(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test AI summary generation."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.full_name = "Test Child"
            mock_child.guardian_id = "guardian-1"
            mock_child.status = ChildStatus.ACTIVE
            mock_child.gender = "male"

            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.full_name = "Jane Doe"
            mock_guardian.email = "jane@example.com"
            mock_guardian.is_active = True

            prediction_service.child_repo.get_by_id = AsyncMock(return_value=mock_child)
            prediction_service.guardian_repo.get_by_id = AsyncMock(return_value=mock_guardian)
            prediction_service.rescue_repo.get_by_child = AsyncMock(return_value=[])
            prediction_service.reunion_repo.get_by_child = AsyncMock(return_value=[])

            result = await prediction_service.generate_ai_summary("child-1", "child")

            assert result.summary_type == "child"
            assert result.entity_id == "child-1"
            assert len(result.overall_assessment) > 0

        anyio.run(run_test)

    def test_generate_recommendations(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test recommendation generation."""
        async def run_test():
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_analysis.id = "analysis-1"
            mock_analysis.incident_id = "incident-1"
            mock_analysis.overall_confidence = 0.85

            prediction_service.analysis_repo.get_by_id = AsyncMock(return_value=mock_analysis)
            prediction_service.match_repo.get_by_incident = AsyncMock(return_value=[])

            result = await prediction_service.generate_recommendations(
                "analysis-1", "analysis"
            )

            assert result.entity_id == "analysis-1"
            assert result.entity_type == "analysis"
            assert len(result.recommendations) > 0

        anyio.run(run_test)

    def test_get_prediction_health(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test prediction health endpoint."""
        async def run_test():
            result = await prediction_service.get_prediction_health()

            assert result.prediction_engine_status == "operational"
            assert result.recommendation_engine_status == "operational"
            assert result.ai_version == "1.0"
            assert len(result.supported_modules) > 0

        anyio.run(run_test)

    def test_missing_entity_returns_default(
        self, prediction_service: PredictionService,
    ) -> None:
        """Test that missing entities return default predictions."""
        async def run_test():
            prediction_service.child_repo.get_by_id = AsyncMock(return_value=None)
            prediction_service.rescue_repo.get_by_id = AsyncMock(return_value=None)
            prediction_service.analysis_repo.get_by_id = AsyncMock(return_value=None)

            reunion = await prediction_service.predict_reunion_probability("nonexistent")
            assert reunion.reunion_probability == 0.0
            assert reunion.confidence == "low"

            rescue = await prediction_service.predict_rescue_success("nonexistent")
            assert rescue.success_probability == 0.0

            risk = await prediction_service.predict_incident_risk("nonexistent")
            assert risk.risk_level == "unknown"

            alert = await prediction_service.predict_alert_probability("nonexistent")
            assert alert.alert_probability == 0.0

            priority = await prediction_service.generate_priority_score("nonexistent")
            assert priority.priority_score == 0.0
            assert priority.priority_level == "low"

        anyio.run(run_test)