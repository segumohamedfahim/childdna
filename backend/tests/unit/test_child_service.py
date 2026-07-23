"""Unit Tests for Child Service"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.child_service import ChildService
from app.schemas.child import ChildCreate, ChildUpdate
from app.core.exceptions import (
    ChildNotFound,
    GuardianNotFound,
    GuardianNotActive,
    InvalidChildData,
)


class TestChildService:
    """Test cases for ChildService"""
    
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def child_service(self, mock_session: AsyncMock) -> ChildService:
        """Create ChildService with mock session"""
        return ChildService(mock_session)
    
    @pytest.fixture
    def mock_child_repository(self, child_service: ChildService) -> MagicMock:
        """Mock child repository"""
        return child_service.repository
    
    @pytest.fixture
    def mock_guardian_repository(self, child_service: ChildService) -> MagicMock:
        """Mock guardian repository"""
        return child_service.guardian_repository
    
    def test_create_child_success(
        self,
        child_service: ChildService,
        mock_child_repository: MagicMock,
        mock_guardian_repository: MagicMock,
    ) -> None:
        """Test successful child creation"""
        async def run_test():
            # Arrange
            guardian_id = "guardian-id"
            child_data = ChildCreate(
                guardian_id=guardian_id,
                full_name="Test child",
                date_of_birth=date.today() - timedelta(days=365),
            )
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.is_active = True
            mock_child = MagicMock()
            mock_child.id = "child-id"
            mock_child.guardian_id = guardian_id
            mock_child.full_name = "Test child"
            mock_child.nickname = None
            mock_child.date_of_birth = date.today() - timedelta(days=365)
            mock_child.gender = None
            mock_child.blood_group = None
            mock_child.allergies = None
            mock_child.medical_notes = None
            mock_child.special_needs = None
            mock_child.emergency_contact_name = None
            mock_child.emergency_contact_phone = None
            mock_child.photo_url = None
            mock_child.status = "active"
            mock_child.created_at = date.today()
            mock_child.updated_at = date.today()
            mock_guardian_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            mock_child_repository.create = AsyncMock(return_value=mock_child)
            
            # Act
            result = await child_service.create_child(child_data)
            
            # Assert
            assert result.guardian_id == guardian_id
            mock_guardian_repository.get_by_id.assert_called_once_with(guardian_id)
            mock_child_repository.create.assert_called_once()
        
        anyio.run(run_test)
    
    def test_create_child_guardian_not_found(
        self,
        child_service: ChildService,
        mock_guardian_repository: MagicMock,
    ) -> None:
        """Test child creation with non-existent guardian"""
        async def run_test():
            # Arrange
            guardian_id = "non-existent-guardian-id"
            child_data = ChildCreate(
                guardian_id=guardian_id,
                full_name="Test child",
                date_of_birth=date.today() - timedelta(days=365),
            )
            mock_guardian_repository.get_by_id = AsyncMock(return_value=None)
            
            # Act & Assert
            with pytest.raises(GuardianNotFound):
                await child_service.create_child(child_data)
        
        anyio.run(run_test)
    
    def test_create_child_guardian_not_active(
        self,
        child_service: ChildService,
        mock_guardian_repository: MagicMock,
    ) -> None:
        """Test child creation with inactive guardian"""
        async def run_test():
            # Arrange
            guardian_id = "inactive-guardian-id"
            child_data = ChildCreate(
                guardian_id=guardian_id,
                full_name="Test child",
                date_of_birth=date.today() - timedelta(days=365),
            )
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.is_active = False
            mock_guardian_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            
            # Act & Assert
            with pytest.raises(GuardianNotActive):
                await child_service.create_child(child_data)
        
        anyio.run(run_test)
    
    def test_create_child_future_dob(
        self,
        child_service: ChildService,
        mock_guardian_repository: MagicMock,
    ) -> None:
        """Test child creation with future date of birth"""
        async def run_test():
            # Arrange
            guardian_id = "guardian-id"
            child_data = ChildCreate(
                guardian_id=guardian_id,
                full_name="Test child",
                date_of_birth=date.today() + timedelta(days=1),
            )
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.is_active = True
            mock_guardian_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            
            # Act & Assert
            with pytest.raises(InvalidChildData):
                await child_service.create_child(child_data)
        
        anyio.run(run_test)
    
    def test_get_child_success(
        self,
        child_service: ChildService,
        mock_child_repository: MagicMock,
    ) -> None:
        """Test successful child retrieval"""
        async def run_test():
            # Arrange
            child_id = "child-id"
            mock_child = MagicMock()
            mock_child.id = child_id
            mock_child.guardian_id = "guardian-id"
            mock_child.full_name = "Test child"
            mock_child.nickname = None
            mock_child.date_of_birth = date.today() - timedelta(days=365)
            mock_child.gender = None
            mock_child.blood_group = None
            mock_child.allergies = None
            mock_child.medical_notes = None
            mock_child.special_needs = None
            mock_child.emergency_contact_name = None
            mock_child.emergency_contact_phone = None
            mock_child.photo_url = None
            mock_child.status = "active"
            mock_child.created_at = date.today()
            mock_child.updated_at = date.today()
            mock_child_repository.get_by_id = AsyncMock(return_value=mock_child)
            
            # Act
            result = await child_service.get_child(child_id)
            
            # Assert
            assert result.id == child_id
            mock_child_repository.get_by_id.assert_called_once_with(child_id)
        
        anyio.run(run_test)
    
    def test_get_child_not_found(
        self,
        child_service: ChildService,
        mock_child_repository: MagicMock,
    ) -> None:
        """Test child retrieval with non-existent ID"""
        async def run_test():
            # Arrange
            child_id = "non-existent-child-id"
            mock_child_repository.get_by_id = AsyncMock(return_value=None)
            
            # Act & Assert
            with pytest.raises(ChildNotFound):
                await child_service.get_child(child_id)
        
        anyio.run(run_test)
    
    def test_update_child_success(
        self,
        child_service: ChildService,
        mock_child_repository: MagicMock,
    ) -> None:
        """Test successful child update"""
        async def run_test():
            # Arrange
            child_id = "child-id"
            update_data = ChildUpdate(nickname="New nickname")
            mock_child = MagicMock()
            mock_child.id = child_id
            mock_child.guardian_id = "guardian-id"
            mock_child.full_name = "Test child"
            mock_child.nickname = "New nickname"
            mock_child.date_of_birth = date.today() - timedelta(days=365)
            mock_child.gender = None
            mock_child.blood_group = None
            mock_child.allergies = None
            mock_child.medical_notes = None
            mock_child.special_needs = None
            mock_child.emergency_contact_name = None
            mock_child.emergency_contact_phone = None
            mock_child.photo_url = None
            mock_child.status = "active"
            mock_child.created_at = date.today()
            mock_child.updated_at = date.today()
            mock_child_repository.get_by_id = AsyncMock(return_value=mock_child)
            mock_child_repository.update = AsyncMock(return_value=mock_child)
            
            # Act
            result = await child_service.update_child(child_id, update_data)
            
            # Assert
            assert result.id == child_id
            mock_child_repository.get_by_id.assert_called_once_with(child_id)
            mock_child_repository.update.assert_called_once()
        
        anyio.run(run_test)
    
    def test_update_child_future_dob(
        self,
        child_service: ChildService,
        mock_child_repository: MagicMock,
    ) -> None:
        """Test child update with future date of birth"""
        async def run_test():
            # Arrange
            child_id = "child-id"
            update_data = ChildUpdate(date_of_birth=date.today() + timedelta(days=1))
            mock_child = MagicMock()
            mock_child.id = child_id
            mock_child_repository.get_by_id = AsyncMock(return_value=mock_child)
            
            # Act & Assert
            with pytest.raises(InvalidChildData):
                await child_service.update_child(child_id, update_data)
        
        anyio.run(run_test)
