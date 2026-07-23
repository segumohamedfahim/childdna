"""Unit Tests for Rescue Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
import anyio
from app.services.rescue_service import RescueService
from app.schemas.rescue_session import RescueSessionCreate, RescueSessionUpdate, RescueSessionResponse
from app.models.enums import SessionStatus, EventType
from app.core.exceptions import (
    ChildNotFound,
    RescueSessionNotFound,
    InvalidSessionStatusTransition,
    ActiveRescueSessionExists,
)


class TestRescueService:
    """Test cases for RescueService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def rescue_service(self, mock_session: AsyncMock) -> RescueService:
        """Create RescueService with mock session"""
        return RescueService(mock_session)

    @pytest.fixture
    def mock_rescue_repo(self, rescue_service: RescueService) -> MagicMock:
        """Mock rescue session repository"""
        return rescue_service.rescue_repo

    @pytest.fixture
    def mock_child_repo(self, rescue_service: RescueService) -> MagicMock:
        """Mock child repository"""
        return rescue_service.child_repo

    @pytest.fixture
    def mock_timeline_service(self, rescue_service: RescueService) -> MagicMock:
        """Mock timeline service"""
        return rescue_service.timeline_service

    def _make_create_data(self, child_id: str = "child-uuid") -> RescueSessionCreate:
        """Create mock create data"""
        return RescueSessionCreate(
            child_id=child_id,
            priority=1,
            rescuer_name="John Rescuer",
            rescuer_phone="+1234567890",
        )

    def _make_mock_incident(
        self,
        incident_id: str = "incident-uuid",
        status: SessionStatus = SessionStatus.PENDING,
    ) -> MagicMock:
        """Create a mock incident"""
        incident = MagicMock()
        incident.id = incident_id
        incident.child_id = "child-uuid"
        incident.status = status
        incident.priority = 1
        incident.rescuer_name = "John Rescuer"
        incident.rescuer_phone = "+1234567890"
        incident.latitude = None
        incident.longitude = None
        incident.location_name = None
        incident.notes = None
        incident.started_at = None
        incident.ended_at = None
        incident.created_at = datetime.now(timezone.utc)
        incident.updated_at = datetime.now(timezone.utc)
        return incident

    def test_create_incident_success(
        self,
        rescue_service: RescueService,
        mock_child_repo: MagicMock,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test successful incident creation"""
        async def run_test():
            # Arrange
            data = self._make_create_data()
            mock_child = MagicMock()
            mock_child.id = "child-uuid"
            mock_child_repo.get_by_id = AsyncMock(return_value=mock_child)
            mock_rescue_repo.has_active_incident = AsyncMock(return_value=False)
            mock_incident = self._make_mock_incident()
            mock_rescue_repo.create = AsyncMock(return_value=mock_incident)
            mock_timeline_service.add_event = AsyncMock()

            # Act
            result = await rescue_service.create_incident(data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_child_repo.get_by_id.assert_called_once_with("child-uuid")
            mock_rescue_repo.has_active_incident.assert_called_once_with("child-uuid")
            mock_rescue_repo.create.assert_called_once_with(data)
            mock_timeline_service.add_event.assert_called_once()

        anyio.run(run_test)

    def test_create_incident_child_not_found(
        self,
        rescue_service: RescueService,
        mock_child_repo: MagicMock,
    ) -> None:
        """Test incident creation with non-existent child"""
        async def run_test():
            # Arrange
            data = self._make_create_data()
            mock_child_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(ChildNotFound):
                await rescue_service.create_incident(data)

        anyio.run(run_test)

    def test_create_incident_duplicate_active(
        self,
        rescue_service: RescueService,
        mock_child_repo: MagicMock,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test incident creation with existing active incident"""
        async def run_test():
            # Arrange
            data = self._make_create_data()
            mock_child = MagicMock()
            mock_child.id = "child-uuid"
            mock_child_repo.get_by_id = AsyncMock(return_value=mock_child)
            mock_rescue_repo.has_active_incident = AsyncMock(return_value=True)

            # Act & Assert
            with pytest.raises(ActiveRescueSessionExists):
                await rescue_service.create_incident(data)

        anyio.run(run_test)

    def test_get_incident_success(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting incident by ID"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(incident_id=incident_id)
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)

            # Act
            result = await rescue_service.get_incident(incident_id)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.get_by_id.assert_called_once_with(incident_id)

        anyio.run(run_test)

    def test_get_incident_not_found(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await rescue_service.get_incident(incident_id)

        anyio.run(run_test)

    def test_list_incidents_pagination(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test listing incidents with pagination"""
        async def run_test():
            # Arrange
            mock_incident = self._make_mock_incident()
            mock_rescue_repo.get_all = AsyncMock(return_value=[mock_incident])

            # Act
            result = await rescue_service.list_incidents(skip=0, limit=10)

            # Assert
            assert len(result) == 1
            mock_rescue_repo.get_all.assert_called_once_with(skip=0, limit=10)

        anyio.run(run_test)

    def test_update_incident_status_pending_to_active(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test valid transition PENDING to ACTIVE"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.PENDING,
            )
            updated_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.ACTIVE,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_rescue_repo.activate = AsyncMock(return_value=updated_incident)
            mock_timeline_service.add_event = AsyncMock()

            update_data = RescueSessionUpdate(status=SessionStatus.ACTIVE)

            # Act
            result = await rescue_service.update_incident(incident_id, update_data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.activate.assert_called_once()
            mock_timeline_service.add_event.assert_called_once()

        anyio.run(run_test)

    def test_update_incident_status_pending_to_cancelled(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test valid transition PENDING to CANCELLED"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.PENDING,
            )
            updated_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.CANCELLED,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_rescue_repo.cancel = AsyncMock(return_value=updated_incident)
            mock_timeline_service.add_event = AsyncMock()

            update_data = RescueSessionUpdate(status=SessionStatus.CANCELLED)

            # Act
            result = await rescue_service.update_incident(incident_id, update_data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.cancel.assert_called_once()
            mock_timeline_service.add_event.assert_called_once()

        anyio.run(run_test)

    def test_update_incident_status_active_to_complete(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test valid transition ACTIVE to COMPLETE"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.ACTIVE,
            )
            updated_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.COMPLETE,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_rescue_repo.complete = AsyncMock(return_value=updated_incident)
            mock_timeline_service.add_event = AsyncMock()

            update_data = RescueSessionUpdate(status=SessionStatus.COMPLETE)

            # Act
            result = await rescue_service.update_incident(incident_id, update_data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.complete.assert_called_once()
            mock_timeline_service.add_event.assert_called_once()

        anyio.run(run_test)

    def test_update_incident_status_active_to_cancelled(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test valid transition ACTIVE to CANCELLED"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.ACTIVE,
            )
            updated_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.CANCELLED,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_rescue_repo.cancel = AsyncMock(return_value=updated_incident)
            mock_timeline_service.add_event = AsyncMock()

            update_data = RescueSessionUpdate(status=SessionStatus.CANCELLED)

            # Act
            result = await rescue_service.update_incident(incident_id, update_data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.cancel.assert_called_once()
            mock_timeline_service.add_event.assert_called_once()

        anyio.run(run_test)

    def test_update_incident_generates_location_event(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
        mock_timeline_service: MagicMock,
    ) -> None:
        """Test updating location generates LOCATION_UPDATED event"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.ACTIVE,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_rescue_repo.update = AsyncMock(return_value=mock_incident)
            mock_timeline_service.add_event = AsyncMock()

            update_data = RescueSessionUpdate(
                latitude=40.7128,
                longitude=-74.0060,
                location_name="Central Park",
            )

            # Act
            result = await rescue_service.update_incident(incident_id, update_data)

            # Assert
            assert isinstance(result, RescueSessionResponse)
            mock_rescue_repo.update.assert_called_once()
            # Verify LOCATION_UPDATED event was generated
            call_args = mock_timeline_service.add_event.call_args
            assert call_args is not None
            assert call_args[1]["event_type"] == EventType.LOCATION_UPDATED

        anyio.run(run_test)

    def test_update_incident_invalid_transition(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test invalid transition PENDING to COMPLETE"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            mock_incident = self._make_mock_incident(
                incident_id=incident_id,
                status=SessionStatus.PENDING,
            )
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)

            update_data = RescueSessionUpdate(status=SessionStatus.COMPLETE)

            # Act & Assert
            with pytest.raises(InvalidSessionStatusTransition):
                await rescue_service.update_incident(incident_id, update_data)

        anyio.run(run_test)

    def test_get_child_incidents_success(
        self,
        rescue_service: RescueService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test getting incidents for a child"""
        async def run_test():
            # Arrange
            child_id = "child-uuid"
            mock_incident = self._make_mock_incident()
            mock_rescue_repo.get_by_child = AsyncMock(return_value=[mock_incident])

            # Act
            result = await rescue_service.get_child_incidents(child_id)

            # Assert
            assert len(result) == 1
            mock_rescue_repo.get_by_child.assert_called_once_with(child_id)

        anyio.run(run_test)