"""Unit Tests for Report Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, date
import anyio
from app.services.report_service import ReportService
from app.core.exceptions import RescueSessionNotFound, AnalysisNotFound
from app.models.child import Child
from app.models.guardian import Guardian
from app.models.rescue_session import RescueSession
from app.models.timeline_event import TimelineEvent
from app.models.reunion_record import ReunionRecord
from app.models.incident_analysis import IncidentAnalysis
from app.models.alert import Alert
from app.models.child_token import ChildToken
from app.models.enums import ChildStatus, SessionStatus


class TestReportService:
    """Test cases for ReportService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def report_service(self, mock_session: AsyncMock) -> ReportService:
        return ReportService(mock_session)

    def test_generate_system_report(
        self, report_service: ReportService,
    ) -> None:
        """Test system report generation."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"

            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.id = "guardian-1"

            mock_rescue = MagicMock(spec=RescueSession)
            mock_rescue.id = "rescue-1"
            mock_rescue.status = SessionStatus.ACTIVE

            mock_reunion = MagicMock(spec=ReunionRecord)
            mock_reunion.id = "reunion-1"

            mock_token = MagicMock(spec=ChildToken)
            mock_token.id = "token-1"

            report_service.child_repo.get_all = AsyncMock(
                return_value=[mock_child]
            )
            report_service.guardian_repo.get_all = AsyncMock(
                return_value=[mock_guardian]
            )
            report_service.rescue_repo.get_all = AsyncMock(
                return_value=[mock_rescue]
            )
            report_service.reunion_repo.get_all = AsyncMock(
                return_value=[mock_reunion]
            )
            report_service.token_repo.get_all = AsyncMock(
                return_value=[mock_token]
            )
            report_service.alert_repo.get_summary = AsyncMock(
                return_value={
                    "by_severity": {"high": 1},
                    "by_status": {"open": 1},
                }
            )

            result = await report_service.generate_system_report()

            assert result.total_children == 1
            assert result.total_guardians == 1
            assert result.total_tokens == 1
            assert result.active_rescues == 1
            assert result.completed_reunions == 1
            assert result.active_alerts == 1
            assert result.metadata.report_type == "system_overview"

        anyio.run(run_test)

    def test_generate_incident_report_success(
        self, report_service: ReportService,
    ) -> None:
        """Test incident report generation."""
        async def run_test():
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_analysis.id = "analysis-1"
            mock_analysis.incident_id = "incident-1"
            mock_analysis.raw_text = "Lost child at the mall"
            mock_analysis.analysis_engine = "rule_engine_v1"
            mock_analysis.overall_confidence = 0.85
            mock_analysis.gender = "male"
            mock_analysis.gender_confidence = 0.95
            mock_analysis.estimated_age_min = 5
            mock_analysis.estimated_age_max = 7
            mock_analysis.created_at = datetime.now(timezone.utc)

            mock_incident = MagicMock(spec=RescueSession)
            mock_incident.id = "incident-1"
            mock_incident.child_id = "child-1"
            mock_incident.status = SessionStatus.ACTIVE
            mock_incident.priority = 1

            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.full_name = "Test Child"

            report_service.analysis_repo.get_by_id = AsyncMock(
                return_value=mock_analysis
            )
            report_service.rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            report_service.child_repo.get_by_id = AsyncMock(
                return_value=mock_child
            )

            result = await report_service.generate_incident_report(
                "analysis-1"
            )

            assert result.incident_id == "incident-1"
            assert result.child_name == "Test Child"
            assert result.overall_confidence == 0.85
            assert result.severity == "high"
            assert len(result.recommendations) > 0
            assert result.metadata.report_type == "incident_analysis"

        anyio.run(run_test)

    def test_generate_incident_report_not_found(
        self, report_service: ReportService,
    ) -> None:
        """Test incident report with non-existent analysis."""
        async def run_test():
            report_service.analysis_repo.get_by_id = AsyncMock(
                return_value=None
            )

            with pytest.raises(AnalysisNotFound):
                await report_service.generate_incident_report(
                    "nonexistent-id"
                )

        anyio.run(run_test)

    def test_generate_rescue_report_success(
        self, report_service: ReportService,
    ) -> None:
        """Test rescue report generation."""
        async def run_test():
            now = datetime.now(timezone.utc)
            mock_incident = MagicMock(spec=RescueSession)
            mock_incident.id = "rescue-1"
            mock_incident.child_id = "child-1"
            mock_incident.status = SessionStatus.COMPLETE
            mock_incident.priority = 2
            mock_incident.rescuer_name = "John Doe"
            mock_incident.rescuer_phone = "1234567890"
            mock_incident.location_name = "Central Park"
            mock_incident.notes = "Child found safe"
            mock_incident.started_at = now
            mock_incident.ended_at = now

            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.full_name = "Test Child"

            mock_event = MagicMock(spec=TimelineEvent)
            mock_event.event_type = "incident_created"
            mock_event.description = "Incident created"
            mock_event.timestamp = now
            mock_event.created_by = "system"

            report_service.rescue_repo.get_by_id = AsyncMock(
                return_value=mock_incident
            )
            report_service.child_repo.get_by_id = AsyncMock(
                return_value=mock_child
            )
            report_service.event_repo.get_by_session = AsyncMock(
                return_value=[mock_event]
            )

            result = await report_service.generate_rescue_report("rescue-1")

            assert result.rescue_id == "rescue-1"
            assert result.child_name == "Test Child"
            assert result.status == "complete"
            assert result.outcome == "successfully completed"
            assert len(result.timeline) == 1
            assert result.metadata.report_type == "rescue_session"

        anyio.run(run_test)

    def test_generate_rescue_report_not_found(
        self, report_service: ReportService,
    ) -> None:
        """Test rescue report with non-existent session."""
        async def run_test():
            report_service.rescue_repo.get_by_id = AsyncMock(
                return_value=None
            )

            with pytest.raises(RescueSessionNotFound):
                await report_service.generate_rescue_report(
                    "nonexistent-id"
                )

        anyio.run(run_test)

    def test_generate_reunion_report_success(
        self, report_service: ReportService,
    ) -> None:
        """Test reunion report generation."""
        async def run_test():
            now = datetime.now(timezone.utc)
            mock_record = MagicMock(spec=ReunionRecord)
            mock_record.id = "reunion-1"
            mock_record.child_id = "child-1"
            mock_record.guardian_name = "Jane Doe"
            mock_record.rescuer_name = "John Doe"
            mock_record.reunion_time = now
            mock_record.verification_method = "id_card"
            mock_record.remarks = "Safe reunion"

            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.full_name = "Test Child"

            report_service.child_repo.get_by_id = AsyncMock(
                return_value=mock_child
            )

            # Mock the reunion_repo.get_by_id
            report_service.reunion_repo.get_by_id = AsyncMock(
                return_value=mock_record
            )

            result = await report_service.generate_reunion_report(
                "reunion-1"
            )

            assert result.reunion_id == "reunion-1"
            assert result.child_name == "Test Child"
            assert result.guardian_name == "Jane Doe"
            assert result.verification_method == "id_card"
            assert result.verification_status == "verified"
            assert result.metadata.report_type == "reunion_record"

        anyio.run(run_test)

    def test_generate_child_report_success(
        self, report_service: ReportService,
    ) -> None:
        """Test child report generation."""
        async def run_test():
            now = datetime.now(timezone.utc)
            mock_child = MagicMock(spec=Child)
            mock_child.id = "child-1"
            mock_child.full_name = "Test Child"
            mock_child.date_of_birth = date(2020, 1, 15)
            mock_child.gender = "male"
            mock_child.blood_group = "A+"
            mock_child.status = ChildStatus.ACTIVE
            mock_child.guardian_id = "guardian-1"

            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.id = "guardian-1"
            mock_guardian.full_name = "Jane Doe"
            mock_guardian.email = "jane@example.com"
            mock_guardian.phone = "1234567890"

            mock_rescue = MagicMock(spec=RescueSession)
            mock_rescue.id = "rescue-1"
            mock_rescue.status = SessionStatus.COMPLETE
            mock_rescue.created_at = now

            mock_event = MagicMock(spec=TimelineEvent)
            mock_event.id = "event-1"

            report_service.child_repo.get_by_id = AsyncMock(
                return_value=mock_child
            )
            report_service.guardian_repo.get_by_id = AsyncMock(
                return_value=mock_guardian
            )
            report_service.rescue_repo.get_by_child = AsyncMock(
                return_value=[mock_rescue]
            )
            report_service.reunion_repo.get_by_child = AsyncMock(
                return_value=[]
            )
            report_service.event_repo.get_by_child = AsyncMock(
                return_value=[mock_event]
            )

            result = await report_service.generate_child_report("child-1")

            assert result.child_id == "child-1"
            assert result.full_name == "Test Child"
            assert result.guardian_name == "Jane Doe"
            assert result.incident_count == 1
            assert result.reunion_count == 0
            assert result.reunion_status == "none"
            assert result.metadata.report_type == "child_profile"

        anyio.run(run_test)

    def test_generate_child_report_not_found(
        self, report_service: ReportService,
    ) -> None:
        """Test child report with non-existent child."""
        async def run_test():
            from app.core.exceptions import ChildNotFound
            report_service.child_repo.get_by_id = AsyncMock(
                return_value=None
            )

            with pytest.raises(ChildNotFound):
                await report_service.generate_child_report(
                    "nonexistent-id"
                )

        anyio.run(run_test)