"""Unit Tests for Analytics Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, date
import anyio
from app.services.analytics_service import AnalyticsService
from app.models.child import Child
from app.models.guardian import Guardian
from app.models.rescue_session import RescueSession
from app.models.reunion_record import ReunionRecord
from app.models.incident_analysis import IncidentAnalysis
from app.models.incident_match import IncidentMatch
from app.models.alert import Alert
from app.models.notification import Notification
from app.models.enums import SessionStatus, ChildStatus


class TestAnalyticsService:
    """Test cases for AnalyticsService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def analytics_service(self, mock_session: AsyncMock) -> AnalyticsService:
        return AnalyticsService(mock_session)

    def test_dashboard_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test dashboard statistics."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_guardian = MagicMock(spec=Guardian)
            mock_rescue = MagicMock(spec=RescueSession)
            mock_reunion = MagicMock(spec=ReunionRecord)
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_match = MagicMock(spec=IncidentMatch)
            mock_alert = MagicMock(spec=Alert)
            mock_notification = MagicMock(spec=Notification)

            for repo in ('child_repo', 'guardian_repo', 'rescue_repo',
                         'reunion_repo', 'analysis_repo', 'match_repo',
                         'alert_repo', 'notification_repo'):
                setattr(getattr(analytics_service, repo), 'get_all',
                        AsyncMock(return_value=[MagicMock()] * 2))

            result = await analytics_service.get_dashboard_statistics()

            assert result.total_children == 2
            assert result.total_guardians == 2
            assert result.total_incidents == 2
            assert result.total_matches == 2
            assert result.total_rescue_sessions == 2
            assert result.total_reunions == 2
            assert result.total_alerts == 2
            assert result.total_notifications == 2

        anyio.run(run_test)

    def test_rescue_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test rescue statistics."""
        async def run_test():
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            mock_active = MagicMock(spec=RescueSession)
            mock_active.status = SessionStatus.ACTIVE
            mock_active.started_at = None
            mock_active.ended_at = None

            mock_complete = MagicMock(spec=RescueSession)
            mock_complete.status = SessionStatus.COMPLETE
            mock_complete.started_at = now
            mock_complete.ended_at = now

            analytics_service.rescue_repo.get_all = AsyncMock(
                return_value=[mock_active, mock_complete]
            )

            result = await analytics_service.get_rescue_statistics()

            assert result.active_rescues == 1
            assert result.completed_rescues == 1
            assert result.failed_rescues == 0
            assert result.success_rate == 100.0

        anyio.run(run_test)

    def test_incident_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test incident statistics."""
        async def run_test():
            mock_analysis = MagicMock(spec=IncidentAnalysis)
            mock_analysis.overall_confidence = 0.85
            mock_rescue = MagicMock(spec=RescueSession)
            mock_rescue.status = SessionStatus.COMPLETE

            analytics_service.analysis_repo.get_all = AsyncMock(
                return_value=[mock_analysis]
            )
            analytics_service.rescue_repo.get_all = AsyncMock(
                return_value=[mock_rescue]
            )

            result = await analytics_service.get_incident_statistics()

            assert result.total_incidents == 1
            assert result.resolved_incidents == 1
            assert result.average_confidence == 0.85
            assert result.severity_distribution.get("high", 0) == 1

        anyio.run(run_test)

    def test_match_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test match statistics."""
        async def run_test():
            mock_match = MagicMock(spec=IncidentMatch)
            mock_match.match_category = "identical"
            mock_match.similarity_score = 0.95

            analytics_service.match_repo.get_all = AsyncMock(
                return_value=[mock_match]
            )

            result = await analytics_service.get_match_statistics()

            assert result.total_matches == 1
            assert result.confirmed_matches == 1
            assert result.average_match_score == 0.95

        anyio.run(run_test)

    def test_alert_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test alert statistics."""
        async def run_test():
            mock_alert = MagicMock(spec=Alert)
            mock_alert.status = "open"
            mock_alert.severity = "high"

            analytics_service.alert_repo.get_all = AsyncMock(
                return_value=[mock_alert]
            )

            result = await analytics_service.get_alert_statistics()

            assert result.total_alerts == 1
            assert result.active_alerts == 1
            assert result.severity_distribution.get("high", 0) == 1

        anyio.run(run_test)

    def test_guardian_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test guardian statistics."""
        async def run_test():
            mock_guardian = MagicMock(spec=Guardian)
            mock_guardian.id = "g-1"
            mock_child = MagicMock(spec=Child)
            mock_child.guardian_id = "g-1"

            analytics_service.guardian_repo.get_all = AsyncMock(
                return_value=[mock_guardian]
            )
            analytics_service.child_repo.get_all = AsyncMock(
                return_value=[mock_child]
            )

            result = await analytics_service.get_guardian_statistics()

            assert result.total_guardians == 1
            assert result.guardians_with_children == 1
            assert result.average_children_per_guardian == 1.0

        anyio.run(run_test)

    def test_child_statistics(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test child statistics."""
        async def run_test():
            mock_child = MagicMock(spec=Child)
            mock_child.status = ChildStatus.ACTIVE
            mock_child.gender = "male"
            mock_child.date_of_birth = date(2020, 1, 1)

            mock_reunion = MagicMock(spec=ReunionRecord)
            mock_reunion.child_id = "child-1"
            mock_child.id = "child-1"

            analytics_service.child_repo.get_all = AsyncMock(
                return_value=[mock_child]
            )
            analytics_service.reunion_repo.get_all = AsyncMock(
                return_value=[mock_reunion]
            )

            result = await analytics_service.get_child_statistics()

            assert result.total_children == 1
            assert result.active_cases == 1
            assert result.reunited_children == 1
            assert result.gender_distribution.get("male", 0) == 1

        anyio.run(run_test)

    def test_system_health(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test system health."""
        async def run_test():
            analytics_service.child_repo.get_all = AsyncMock(
                return_value=[]
            )

            result = await analytics_service.get_system_health()

            assert result.database_status == "operational"
            assert result.analytics_status == "operational"
            assert result.authentication_status == "operational"

        anyio.run(run_test)

    def test_empty_database(
        self, analytics_service: AnalyticsService,
    ) -> None:
        """Test empty database returns zeros."""
        async def run_test():
            for repo in ('child_repo', 'guardian_repo', 'rescue_repo',
                         'reunion_repo', 'analysis_repo', 'match_repo',
                         'alert_repo', 'notification_repo'):
                setattr(getattr(analytics_service, repo), 'get_all',
                        AsyncMock(return_value=[]))

            result = await analytics_service.get_dashboard_statistics()

            assert result.total_children == 0
            assert result.total_guardians == 0
            assert result.total_incidents == 0
            assert result.total_matches == 0
            assert result.total_rescue_sessions == 0
            assert result.total_reunions == 0
            assert result.total_alerts == 0
            assert result.total_notifications == 0

        anyio.run(run_test)