"""API Endpoint Tests for Guardian"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.schemas.guardian import GuardianCreate, GuardianUpdate, GuardianResponse


class TestGuardianEndpoints:
    """Test cases for Guardian API endpoints"""
    
    def test_create_guardian_success(self, client: TestClient) -> None:
        """Test successful guardian creation via API"""
        # Arrange
        guardian_data = {
            "email": "test@example.com",
            "full_name": "Test user",
            "phone": "1234567890",
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.guardian.GuardianService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.create_guardian = AsyncMock(
                return_value=GuardianResponse(
                    id="test-id",
                    email=guardian_data["email"],
                    full_name=guardian_data["full_name"],
                    phone=guardian_data["phone"],
                    is_active=True,
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/guardians", json=guardian_data)
        
        # Assert
        assert response.status_code == 201
    
    def test_create_guardian_duplicate_email(self, client: TestClient) -> None:
        """Test guardian creation with duplicate email via API"""
        # Arrange
        guardian_data = {
            "email": "existing@example.com",
            "full_name": "Test user",
        }
        
        # Act
        with patch(
            "app.api.v1.endpoints.guardian.GuardianService"
        ) as mock_service_class:
            from app.core.exceptions import GuardianAlreadyExists
            mock_service = AsyncMock()
            mock_service.create_guardian = AsyncMock(
                side_effect=GuardianAlreadyExists(email=guardian_data["email"])
            )
            mock_service_class.return_value = mock_service
            
            response = client.post("/api/v1/guardians", json=guardian_data)
        
        # Assert
        assert response.status_code == 409
    
    def test_get_guardian_success(
        self, client: TestClient, admin_auth_header: dict
    ) -> None:
        """Test successful guardian retrieval via API"""
        # Arrange
        guardian_id = "test-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.guardian.GuardianService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_guardian = AsyncMock(
                return_value=GuardianResponse(
                    id=guardian_id,
                    email="test@example.com",
                    full_name="Test user",
                    is_active=True,
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.get(
                f"/api/v1/guardians/{guardian_id}",
                headers=admin_auth_header,
            )
        
        # Assert
        assert response.status_code == 200
    
    def test_get_guardian_not_found(
        self, client: TestClient, admin_auth_header: dict
    ) -> None:
        """Test guardian retrieval with non-existent ID via API"""
        # Arrange
        guardian_id = "non-existent-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.guardian.GuardianService"
        ) as mock_service_class:
            from app.core.exceptions import GuardianNotFound
            mock_service = AsyncMock()
            mock_service.get_guardian = AsyncMock(
                side_effect=GuardianNotFound(guardian_id=guardian_id)
            )
            mock_service_class.return_value = mock_service
            
            response = client.get(
                f"/api/v1/guardians/{guardian_id}",
                headers=admin_auth_header,
            )
        
        # Assert
        assert response.status_code == 404
