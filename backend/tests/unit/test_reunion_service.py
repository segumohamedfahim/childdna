"""Unit Tests for Reunion Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
import anyio
from app.services.reunion_service import ReunionService
from app.schemas.reunion_record import ReunionRecordCreate, ReunionRecordResponse
from app.models.enums import SessionStatus
from app.core.exceptions import (
    ChildNotFound,
    RescueSessionNotFound,
    InvalidSessionStatusTransition,
)


class TestReunionService:
    """Test cases for ReunionService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def reunion_service(self, mock_session: AsyncMock) -> ReunionService:
        """Create ReunionService with mock session"""
        return ReunionService(mock_session)

    @pytest.fixture
    def mock_reunion_repo(self, reunion_service: ReunionService) -> MagicMock:
        """Mock reunion repository"""
        return reunion_service.reunion_repo

    @pytest.fixture
    def mock_rescue_repo(self, reunion_service: ReunionService) -> MagicMock:
        """Mock rescue repository"""
        return reunion_service.rescue_repo

    @pytest.fixture
    def mock_child_repo(self, reunion_service: ReunionService) -> MagicMock:
        """Mock child repository"""
        return reunion_service.child_repo

    @pytest.fixture
    def mock_event_repo(self, reunion_service: ReunionService) -> MagicMock:
        """Mock event repository"""
        return reunion_service.event_repo

    def _make_reunion_data(self) -> ReunionRecordCreate:
        """Create mock reunion data"""
        return ReunionRecordCreate(
            child_id="child-uuid",
            rescuer_name="John Rescuer",
            guardian_name="Jane Doe",
            reunion_time="2026-07-23T14:30:00Z",
            verification_method="guardian_id_card",
        )

    def test_record_reunion_success(
        self,
        reunion_service: ReunionService,
        mock_rescue_repo: MagicMock,
        mock_child_repo: MagicMock,
        mock_reunion_repo: MagicMock,
        mock_event_repo: MagicMock,
    ) -> None:
        """Test successful reunion recording"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            data = self._make_reunion_data()
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_incident.status = SessionStatus.ACTIVE
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_child = MagicMock()
            mock_child.id = "child-uuid"
            mock_child_repo.get_by_id = AsyncMock(return_value=mock_child)
            mock_reunion = MagicMock()
            mock_reunion.id = "reunion-uuid"
            mock_reunion.child_id = "child-uuid"
            mock_reunion.rescuer_name = "John Rescuer"
            mock_reunion.guardian_name = "Jane Doe"
            mock_reunion.reunion_time = datetime.now(timezone.utc)
            mock_reunion.verification_method = "guardian_id_card"
            mock_reunion.remarks = None
            mock_reunion.created_at = datetime.now(timezone.utc)
            mock_reunion_repo.create = AsyncMock(return_value=mock_reunion)
            mock_event_repo.create = AsyncMock()
            mock_rescue_repo.complete = AsyncMock()

            # Act
            result = await reunion_service.record_reunion(incident_id, data)

            # Assert
            assert isinstance(result, ReunionRecordResponse)
            mock_rescue_repo.complete.assert_called_once()
            mock_event_repo.create.assert_called_once()

        anyio.run(run_test)

    def test_record_reunion_incident_not_found(
        self,
        reunion_service: ReunionService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test reunion with non-existent incident"""
        async def run_test():
            # Arrange
            incident_id = "nonexistent-uuid"
            data = self._make_reunion_data()
            mock_rescue_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(RescueSessionNotFound):
                await reunion_service.record_reunion(incident_id, data)

        anyio.run(run_test)

    def test_record_reunion_incident_not_active(
        self,
        reunion_service: ReunionService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test reunion with non-active incident"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            data = self._make_reunion_data()
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_incident.status = SessionStatus.PENDING
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)

            # Act & Assert
            with pytest.raises(InvalidSessionStatusTransition):
                await reunion_service.record_reunion(incident_id, data)

        anyio.run(run_test)

    def test_record_reunion_complete_incident(
        self,
        reunion_service: ReunionService,
        mock_rescue_repo: MagicMock,
    ) -> None:
        """Test reunion with already COMPLETE incident"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            data = self._make_reunion_data()
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_incident.status = SessionStatus.COMPLETE
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)

            # Act & Assert
            with pytest.raises(InvalidSessionStatusTransition):
                await reunion_service.record_reunion(incident_id, data)

        anyio.run(run_test)

    def test_record_reunion_child_not_found(
        self,
        reunion_service: ReunionService,
        mock_rescue_repo: MagicMock,
        mock_child_repo: MagicMock,
    ) -> None:
        """Test reunion with non-existent child"""
        async def run_test():
            # Arrange
            incident_id = "incident-uuid"
            data = self._make_reunion_data()
            mock_incident = MagicMock()
            mock_incident.id = incident_id
            mock_incident.child_id = "child-uuid"
            mock_incident.status = SessionStatus.ACTIVE
            mock_rescue_repo.get_by_id = AsyncMock(return_value=mock_incident)
            mock_child_repo.get_by_id = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(ChildNotFound):
                await reunion_service.record_reunion(incident_id, data)

        anyio.run(run_test)

    def test_get_child_reunions_success(
        self,
        reunion_service: ReunionService,
        mock_reunion_repo: MagicMock,
    ) -> None:
        """Test getting reunions for a child"""
        async def run_test():
            # Arrange
            child_id = "child-uuid"
            mock_record = MagicMock()
            mock_record.id = "reunion-uuid"
            mock_record.child_id = "child-uuid"
            mock_record.rescuer_name = "John Rescuer"
            mock_record.guardian_name = "Jane Doe"
            mock_record.reunion_time = datetime.now(timezone.utc)
            mock_record.verification_method = "guardian_id_card"
            mock_record.remarks = None
            mock_record.created_at = datetime.now(timezone.utc)
            mock_reunion_repo.get_by_child = AsyncMock(return_value=[mock_record])

            # Act
            result = await reunion_service.get_child_reunions(child_id)

            # Assert
            assert len(result) == 1
            assert isinstance(result[0], ReunionRecordResponse)
            mock_reunion_repo.get_by_child.assert_called_once_with(child_id)

        anyio.run(run_test)
