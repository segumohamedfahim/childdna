"""Unit Tests for Timeline Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
import anyio
from app.services.timeline_service import TimelineService
from app.schemas.timeline_event import TimelineEventResponse
from app.models.enums import EventType
from app.core.exceptions import RescueSessionNotFound


class TestTimelineService:
    """Test cases for TimelineService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def timeline_service(self, mock_session: AsyncMock) -> TimelineService:
        """Create TimelineService with mock session"""
        return TimelineService(mock_session)

    @pytest.fixture
    def mock_event_repo(self, timeline_service: TimelineService) -> MagicMock:
        """Mock event repository"""
        return timeline_service.event_repo

    @pytest.fixture
    def mock_rescue_repo(self, timeline_service: TimelineService) -> MagicMock:
        """Mock rescue repository"""
        return timeline_service.rescue_repo

    def test_get_incident_timeline_success(
        self,
        timeline_service: TimelineService,
        mock_rescue_repo: MagicMock,
        mock_event_repo: MagicMock,
    ) -> None:
        """Test getting timeline for an incident"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_event = MagicMock()
            mock_event.id = "event-uuid"
            mock_event.child_id = "child-uuid"
            mock_event.rescue_session_id = incident_id
            mock_event.event_type = EventType.INCIDENT_CREATED
            mock_event.description = "Test event"
            mock_event.created_by = "system"
            mock_event.latitude = None
            mock_event.longitude = None
            mock_event.location_name = None
            mock_event.timestamp = datetime.now(timezone.utc)
            mock_event.created_at = datetime.now(timezone.utc)
            mock_event_repo.get_by_session = AsyncMock(return_value=[mock_event])

            # Act
            result = await timeline_service.get_incident_timeline(incident_id)

            # Assert
            assert len(result) == 1
            assert isinstance(result[0], TimelineEventResponse)
            mock_rescue_repo.get_by_id.assert_called_once_with(incident_id)
            mock_event_repo.get_by_session.assert_called_once_with(incident_id)

        anyio.run(run_test)

    def test_get_incident_timeline_incident_not_found(
        self,
        timeline_service: TimelineService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting timeline for non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await timeline_service.get_incident_timeline(incident_id)

        anyio.run(run_test)

    def test_get_incident_timeline_empty(
        self,
        timeline_service: TimelineService,
        mock_rescue_repo: MagicMock,
        mock_event_repo: MagicMock,
    ) -> None:
        """Test getting timeline for incident with no events"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_event_repo.get_by_session = AsyncMock(return_value=[])

            # Act
            result = await timeline_service.get_incident_timeline(incident_id)

            # Assert
            assert len(result) == 0

        anyio.run(run_test)