"""Unit Tests for Guardian Service"""
import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
import anyio
from app.services.guardian_service import GuardianService
from app.schemas.guardian import GuardianCreate, GuardianUpdate
from app.core.exceptions import GuardianAlreadyExists, GuardianNotFound


class TestGuardianService:
    """Test cases for GuardianService"""
    
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def guardian_service(self, mock_session: AsyncMock) -> GuardianService:
        """Create GuardianService with mock session"""
        return GuardianService(mock_session)
    
    @pytest.fixture
    def mock_repository(self, guardian_service: GuardianService) -> MagicMock:
        """Mock repository"""
        return guardian_service.repository
    
    def test_create_guardian_success(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test successful guardian creation"""
        async def run_test():
            # Arrange
            guardian_data = GuardianCreate(
                email="test@example.com",
                full_name="Test user",
                phone="1234567890",
            )
            mock_guardian = MagicMock()
            mock_guardian.id = "test-id"
            mock_guardian.email = guardian_data.email
            mock_guardian.full_name = guardian_data.full_name
            mock_guardian.phone = guardian_data.phone
            mock_guardian.alternate_phone = None
            mock_guardian.address = None
            mock_guardian.preferred_language = "en"
            mock_guardian.is_active = True
            mock_guardian.created_at = date.today()
            mock_guardian.updated_at = date.today()
            mock_repository.get_by_email = AsyncMock(return_value=None)
            mock_repository.create = AsyncMock(return_value=mock_guardian)
            
            # Act
            result = await guardian_service.create_guardian(guardian_data)
            
            # Assert
            assert result.email == guardian_data.email
            mock_repository.get_by_email.assert_called_once_with(guardian_data.email)
            mock_repository.create.assert_called_once()
        
        anyio.run(run_test)
    
    def test_create_guardian_duplicate_email(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test guardian creation with duplicate email"""
        async def run_test():
            # Arrange
            guardian_data = GuardianCreate(
                email="existing@example.com",
                full_name="Test user",
            )
            mock_existing_guardian = MagicMock()
            mock_existing_guardian.id = "existing-id"
            mock_repository.get_by_email = AsyncMock(return_value=mock_existing_guardian)
            
            # Act & Assert
            with pytest.raises(GuardianAlreadyExists):
                await guardian_service.create_guardian(guardian_data)
        
        anyio.run(run_test)
    
    def test_get_guardian_success(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test successful guardian retrieval"""
        async def run_test():
            # Arrange
            guardian_id = "test-id"
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.email = "test@example.com"
            mock_guardian.full_name = "Test user"
            mock_guardian.phone = "1234567890"
            mock_guardian.alternate_phone = None
            mock_guardian.address = None
            mock_guardian.preferred_language = "en"
            mock_guardian.is_active = True
            mock_guardian.created_at = date.today()
            mock_guardian.updated_at = date.today()
            mock_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            
            # Act
            result = await guardian_service.get_guardian(guardian_id)
            
            # Assert
            assert result.id == guardian_id
            mock_repository.get_by_id.assert_called_once_with(guardian_id)
        
        anyio.run(run_test)
    
    def test_get_guardian_not_found(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test guardian retrieval with non-existent ID"""
        async def run_test():
            # Arrange
            guardian_id = "non-existent-id"
            mock_repository.get_by_id = AsyncMock(return_value=None)
            
            # Act & Assert
            with pytest.raises(GuardianNotFound):
                await guardian_service.get_guardian(guardian_id)
        
        anyio.run(run_test)
    
    def test_update_guardian_success(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test successful guardian update"""
        async def run_test():
            # Arrange
            guardian_id = "test-id"
            update_data = GuardianUpdate(full_name="Updated name")
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.email = "test@example.com"
            mock_guardian.full_name = "Updated name"
            mock_guardian.phone = "1234567890"
            mock_guardian.alternate_phone = None
            mock_guardian.address = None
            mock_guardian.preferred_language = "en"
            mock_guardian.is_active = True
            mock_guardian.created_at = date.today()
            mock_guardian.updated_at = date.today()
            mock_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            mock_repository.update = AsyncMock(return_value=mock_guardian)
            
            # Act
            result = await guardian_service.update_guardian(guardian_id, update_data)
            
            # Assert
            assert result.id == guardian_id
            mock_repository.get_by_id.assert_called_once_with(guardian_id)
            mock_repository.update.assert_called_once()
        
        anyio.run(run_test)
    
    def test_deactivate_guardian_success(
        self, guardian_service: GuardianService, mock_repository: MagicMock
    ) -> None:
        """Test successful guardian deactivation"""
        async def run_test():
            # Arrange
            guardian_id = "test-id"
            mock_guardian = MagicMock()
            mock_guardian.id = guardian_id
            mock_guardian.is_active = True
            mock_repository.get_by_id = AsyncMock(return_value=mock_guardian)
            mock_repository.delete = AsyncMock()
            
            # Act
            await guardian_service.deactivate_guardian(guardian_id)
            
            # Assert
            mock_repository.get_by_id.assert_called_once_with(guardian_id)
            mock_repository.delete.assert_called_once()
        
        anyio.run(run_test)
