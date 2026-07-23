"""API Endpoint Tests for Child"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse


class TestChildEndpoints:
    """Test cases for Child API endpoints"""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)
    
    def test_create_child_success(self, client: TestClient) -> None:
        """Test successful child creation via API"""
        # Arrange
        child_data = {
            "guardian_id": "guardian-id",
            "full_name": "Test child",
            "date_of_birth": (date.today() - timedelta(days=365)).isoformat(),
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.create_child = AsyncMock(
                return_value=ChildResponse(
                    id="child-id",
                    guardian_id=child_data["guardian_id"],
                    full_name=child_data["full_name"],
                    date_of_birth=date.today() - timedelta(days=365),
                    status="active",
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/children", json=child_data)
        
        # Assert
        assert response.status_code == 201
    
    def test_create_child_guardian_not_found(self, client: TestClient) -> None:
        """Test child creation with non-existent guardian via API"""
        # Arrange
        child_data = {
            "guardian_id": "non-existent-guardian-id",
            "full_name": "Test child",
            "date_of_birth": (date.today() - timedelta(days=365)).isoformat(),
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            from app.core.exceptions import GuardianNotFound
            mock_service = AsyncMock()
            mock_service.create_child = AsyncMock(
                side_effect=GuardianNotFound(guardian_id=child_data["guardian_id"])
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/children", json=child_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_create_child_guardian_not_active(self, client: TestClient) -> None:
        """Test child creation with inactive guardian via API"""
        # Arrange
        child_data = {
            "guardian_id": "inactive-guardian-id",
            "full_name": "Test child",
            "date_of_birth": (date.today() - timedelta(days=365)).isoformat(),
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            from app.core.exceptions import GuardianNotActive
            mock_service = AsyncMock()
            mock_service.create_child = AsyncMock(
                side_effect=GuardianNotActive(guardian_id=child_data["guardian_id"])
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/children", json=child_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_create_child_future_dob(self, client: TestClient) -> None:
        """Test child creation with future date of birth via API"""
        # Arrange
        child_data = {
            "guardian_id": "guardian-id",
            "full_name": "Test child",
            "date_of_birth": (date.today() + timedelta(days=1)).isoformat(),
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            from app.core.exceptions import InvalidChildData
            mock_service = AsyncMock()
            mock_service.create_child = AsyncMock(
                side_effect=InvalidChildData(
                    message="Date of birth cannot be in the future"
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/children", json=child_data)
        
        # Assert
        assert response.status_code == 400
    
    def test_get_child_success(self, client: TestClient) -> None:
        """Test successful child retrieval via API"""
        # Arrange
        child_id = "child-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_child = AsyncMock(
                return_value=ChildResponse(
                    id=child_id,
                    guardian_id="guardian-id",
                    full_name="Test child",
                    date_of_birth=date.today() - timedelta(days=365),
                    status="active",
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/children/{child_id}")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_child_not_found(self, client: TestClient) -> None:
        """Test child retrieval with non-existent ID via API"""
        # Arrange
        child_id = "non-existent-child-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.child.ChildService"
        ) as mock_service_class:
            from app.core.exceptions import ChildNotFound
            mock_service = AsyncMock()
            mock_service.get_child = AsyncMock(
                side_effect=ChildNotFound(child_id=child_id)
            )
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/children/{child_id}")
        
        # Assert
        assert response.status_code == 404
