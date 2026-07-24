"""Unit Tests for Alert Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.alert_service import AlertService
from app.schemas.alert import (
    AlertResponse,
    AlertListResponse,
    AlertSummaryResponse,
)
from app.core.exceptions import AlertNotFound, InvalidAlertStatusTransition


class TestAlertService:
    """Test cases for AlertService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def alert_service(self, mock_session: AsyncMock) -> AlertService:
        """Create AlertService with mock session"""
        return AlertService(mock_session)

    @pytest.fixture
    def mock_alert_repo(
        self, alert_service: AlertService,
    ) -> MagicMock:
        """Mock alert repository"""
        return alert_service.alert_repo

    def _make_alert_mock(
        self, status: str = "open", **kwargs
    ) -> MagicMock:
        """Helper to create alert mock with proper string values"""
        alert = MagicMock()
        alert.id = kwargs.get("id", "alert-uuid-123")
        alert.incident_id = kwargs.get("incident_id", "incident-uuid-123")
        alert.matched_incident_id = kwargs.get("matched_incident_id", None)
        alert.alert_type = kwargs.get("alert_type", "match_found")
        alert.severity = kwargs.get("severity", "high")
        alert.status = status
        alert.title = kwargs.get("title", "Test Alert")
        alert.description = kwargs.get("description", "A test alert description")
        alert.source = kwargs.get("source", "matching_engine")
        alert.extra_data = kwargs.get("extra_data", None)
        alert.acknowledged_by = kwargs.get("acknowledged_by", None)
        alert.acknowledged_at = kwargs.get("acknowledged_at", None)
        alert.resolved_by = kwargs.get("resolved_by", None)
        alert.resolved_at = kwargs.get("resolved_at", None)
        alert.created_at = kwargs.get("created_at", None)
        alert.updated_at = kwargs.get("updated_at", None)
        return alert

    def test_create_alert_success(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test successful alert creation"""
        async def run_test():
            sample = self._make_alert_mock()
            mock_alert_repo.exists = AsyncMock(return_value=False)
            mock_alert_repo.create = AsyncMock(return_value=sample)

            result = await alert_service.create_alert(
                incident_id="incident-uuid-123",
                matched_incident_id=None,
                alert_type="match_found",
                severity="high",
                title="Test Alert",
                description="A test alert description",
            )

            assert isinstance(result, AlertResponse)
            assert result.id == "alert-uuid-123"
            assert result.severity == "high"
            assert result.status == "open"
            assert result.alert_type == "match_found"
            mock_alert_repo.exists.assert_awaited_once()
            mock_alert_repo.create.assert_awaited_once()

        anyio.run(run_test)

    def test_create_alert_dedup(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test duplicate alert prevention"""
        async def run_test():
            sample = self._make_alert_mock()
            mock_alert_repo.exists = AsyncMock(return_value=True)
            mock_alert_repo.get_by_incident = AsyncMock(
                return_value=[sample]
            )
            mock_alert_repo.create = AsyncMock()

            result = await alert_service.create_alert(
                incident_id="incident-uuid-123",
                matched_incident_id=None,
                alert_type="match_found",
                severity="high",
                title="Test Alert",
                description="A test alert description",
            )

            assert isinstance(result, AlertResponse)
            assert result.id == "alert-uuid-123"
            mock_alert_repo.create.assert_not_called()

        anyio.run(run_test)

    def test_get_alert_success(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test successful alert retrieval"""
        async def run_test():
            sample = self._make_alert_mock()
            mock_alert_repo.get_by_id = AsyncMock(return_value=sample)

            result = await alert_service.get_alert("alert-uuid-123")

            assert isinstance(result, AlertResponse)
            assert result.id == "alert-uuid-123"
            mock_alert_repo.get_by_id.assert_awaited_once_with("alert-uuid-123")

        anyio.run(run_test)

    def test_get_alert_not_found(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test alert not found raises exception"""
        async def run_test():
            mock_alert_repo.get_by_id = AsyncMock(return_value=None)

            with pytest.raises(AlertNotFound):
                await alert_service.get_alert("nonexistent-uuid")

        anyio.run(run_test)

    def test_list_alerts_no_filter(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test listing alerts without filters"""
        async def run_test():
            sample = self._make_alert_mock()
            mock_alert_repo.get_all = AsyncMock(return_value=[sample])

            result = await alert_service.list_alerts()

            assert isinstance(result, AlertListResponse)
            assert len(result.alerts) == 1
            assert result.alerts[0].id == "alert-uuid-123"

        anyio.run(run_test)

    def test_list_alerts_filter_by_status(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test listing alerts filtered by status"""
        async def run_test():
            sample = self._make_alert_mock()
            mock_alert_repo.get_by_status = AsyncMock(
                return_value=[sample]
            )

            result = await alert_service.list_alerts(status="open")

            assert isinstance(result, AlertListResponse)
            assert len(result.alerts) == 1
            mock_alert_repo.get_by_status.assert_awaited_once_with(
                "open", 0, 20
            )

        anyio.run(run_test)

    def test_acknowledge_alert_success(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test successful alert acknowledgement"""
        async def run_test():
            sample = self._make_alert_mock(status="open")
            mock_alert_repo.get_by_id = AsyncMock(return_value=sample)
            updated = self._make_alert_mock(
                status="acknowledged",
                acknowledged_by="Officer Smith",
                acknowledged_at=None,
            )
            mock_alert_repo.update_status = AsyncMock(return_value=updated)

            result = await alert_service.acknowledge_alert(
                "alert-uuid-123", "Officer Smith"
            )

            assert result.status == "acknowledged"
            mock_alert_repo.update_status.assert_awaited_once()

        anyio.run(run_test)

    def test_acknowledge_alert_invalid_transition(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test acknowledging a non-open alert raises error"""
        async def run_test():
            closed = self._make_alert_mock(status="resolved")
            mock_alert_repo.get_by_id = AsyncMock(return_value=closed)

            with pytest.raises(InvalidAlertStatusTransition):
                await alert_service.acknowledge_alert(
                    "alert-uuid-123", "Officer Smith"
                )

        anyio.run(run_test)

    def test_resolve_alert_success(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test successful alert resolution"""
        async def run_test():
            acknowledged = self._make_alert_mock(status="acknowledged")
            mock_alert_repo.get_by_id = AsyncMock(
                return_value=acknowledged
            )
            resolved = self._make_alert_mock(
                status="resolved",
                resolved_by="Officer Smith",
                resolved_at=None,
            )
            mock_alert_repo.update_status = AsyncMock(
                return_value=resolved
            )

            result = await alert_service.resolve_alert(
                "alert-uuid-123", "Officer Smith"
            )

            assert result.status == "resolved"
            mock_alert_repo.update_status.assert_awaited_once()

        anyio.run(run_test)

    def test_dismiss_alert_success(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test successful alert dismissal"""
        async def run_test():
            open_alert = self._make_alert_mock(status="open")
            mock_alert_repo.get_by_id = AsyncMock(return_value=open_alert)
            dismissed = self._make_alert_mock(status="dismissed")
            mock_alert_repo.update_status = AsyncMock(
                return_value=dismissed
            )

            result = await alert_service.dismiss_alert(
                "alert-uuid-123", "Officer Smith"
            )

            assert result.status == "dismissed"
            mock_alert_repo.update_status.assert_awaited_once()

        anyio.run(run_test)

    def test_dismiss_alert_from_terminal_state(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test dismissing already resolved alert raises error"""
        async def run_test():
            resolved = self._make_alert_mock(status="resolved")
            mock_alert_repo.get_by_id = AsyncMock(
                return_value=resolved
            )

            with pytest.raises(InvalidAlertStatusTransition):
                await alert_service.dismiss_alert(
                    "alert-uuid-123", "Officer Smith"
                )

        anyio.run(run_test)

    def test_get_alert_summary(
        self,
        alert_service: AlertService,
        mock_alert_repo: MagicMock,
    ) -> None:
        """Test alert summary retrieval"""
        async def run_test():
            mock_alert_repo.get_summary = AsyncMock(
                return_value={
                    "by_severity": {"high": 3, "low": 1},
                    "by_status": {
                        "open": 2, "acknowledged": 1, "resolved": 1,
                    },
                }
            )

            result = await alert_service.get_alert_summary()

            assert isinstance(result, AlertSummaryResponse)
            assert result.total_open == 2
            assert result.total_acknowledged == 1
            assert result.total_resolved == 1
            assert result.total_dismissed == 0
            assert result.by_severity == {"high": 3, "low": 1}

        anyio.run(run_test)

    def test_determine_severity(self) -> None:
        """Test match category to severity mapping"""
        assert AlertService.determine_severity("identical") == "critical"
        assert AlertService.determine_severity("very_high") == "high"
        assert AlertService.determine_severity("high") == "medium"
        assert AlertService.determine_severity("medium") == "low"
        assert AlertService.determine_severity("low") == "low"
        assert AlertService.determine_severity("no_match") == "low"
        assert AlertService.determine_severity("unknown") == "low"

    def test_build_alert_title(self) -> None:
        """Test alert title generation from match data"""
        title = AlertService.build_alert_title("identical", 0.95)
        assert "Identical Match" in title
        assert "95.0%" in title

        title = AlertService.build_alert_title("unknown", 0.5)
        assert "Potential Match" in title