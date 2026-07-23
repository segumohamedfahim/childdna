"""API Endpoint Tests for Token"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

import pytest
from datetime import date
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from app.schemas.child_token import ChildTokenResponse
from app.models.enums import TokenStatus


class TestTokenEndpoints:
    """Test cases for Token API endpoints"""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)
    
    def test_create_token_success(self, client: TestClient) -> None:
        """Test successful token creation via API"""
        # Arrange
        child_id = "test-child-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.generate_token = AsyncMock(
                return_value=ChildTokenResponse(
                    id="token-id",
                    child_id=child_id,
                    token_code="DNA-ABCD-EFGH",
                    qr_secret="test-secret",
                    status=TokenStatus.ISSUED,
                    issued_at=date.today(),
                    expires_at=None,
                    last_scanned_at=None,
                    revoked_at=None,
                    is_active=True,
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/children/{child_id}/tokens")
        
        # Assert
        assert response.status_code == 201
    
    def test_list_child_tokens_success(self, client: TestClient) -> None:
        """Test successful token list retrieval via API"""
        # Arrange
        child_id = "test-child-id"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_child_tokens = AsyncMock(
                return_value=[
                    ChildTokenResponse(
                        id="token-id",
                        child_id=child_id,
                        token_code="DNA-ABCD-EFGH",
                        qr_secret="test-secret",
                        status=TokenStatus.ACTIVE,
                        issued_at=date.today(),
                        expires_at=None,
                        last_scanned_at=None,
                        revoked_at=None,
                        is_active=True,
                        created_at=date.today(),
                        updated_at=date.today(),
                    )
                ]
            )
            mock_service_class.return_value = mock_service
            
            response = client.get(f"/api/v1/children/{child_id}/tokens")
        
        # Assert
        assert response.status_code == 200
    
    def test_activate_token_success(self, client: TestClient) -> None:
        """Test successful token activation via API"""
        # Arrange
        token_code = "DNA-ABCD-EFGH"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.activate_token = AsyncMock(
                return_value=ChildTokenResponse(
                    id="token-id",
                    child_id="child-id",
                    token_code=token_code,
                    qr_secret="test-secret",
                    status=TokenStatus.ACTIVE,
                    issued_at=date.today(),
                    expires_at=None,
                    last_scanned_at=None,
                    revoked_at=None,
                    is_active=True,
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/tokens/{token_code}/activate")
        
        # Assert
        assert response.status_code == 200
    
    def test_activate_token_already_active(self, client: TestClient) -> None:
        """Test activation of already active token via API"""
        # Arrange
        token_code = "DNA-ABCD-EFGH"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            from app.core.exceptions import TokenAlreadyActive
            mock_service = AsyncMock()
            mock_service.activate_token = AsyncMock(
                side_effect=TokenAlreadyActive(token_code=token_code)
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/tokens/{token_code}/activate")
        
        # Assert
        assert response.status_code == 400
    
    def test_activate_token_invalid_format(self, client: TestClient) -> None:
        """Test activation with invalid token format via API"""
        # Arrange
        token_code = "invalid-token"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            from app.core.exceptions import InvalidTokenFormat
            mock_service = AsyncMock()
            mock_service.activate_token = AsyncMock(
                side_effect=InvalidTokenFormat(token_code=token_code)
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/tokens/{token_code}/activate")
        
        # Assert
        assert response.status_code == 400
    
    def test_revoke_token_success(self, client: TestClient) -> None:
        """Test successful token revocation via API"""
        # Arrange
        token_code = "DNA-ABCD-EFGH"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.revoke_token = AsyncMock(
                return_value=ChildTokenResponse(
                    id="token-id",
                    child_id="child-id",
                    token_code=token_code,
                    qr_secret="test-secret",
                    status=TokenStatus.REVOKED,
                    issued_at=date.today(),
                    expires_at=None,
                    last_scanned_at=None,
                    revoked_at=date.today(),
                    is_active=True,
                    created_at=date.today(),
                    updated_at=date.today(),
                )
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/tokens/{token_code}/revoke")
        
        # Assert
        assert response.status_code == 200
    
    def test_revoke_token_already_revoked(self, client: TestClient) -> None:
        """Test revocation of already revoked token via API"""
        # Arrange
        token_code = "DNA-ABCD-EFGH"
        
        # Act
        with patch(
            "app.api.v1.endpoints.token.TokenService"
        ) as mock_service_class:
            from app.core.exceptions import TokenAlreadyRevoked
            mock_service = AsyncMock()
            mock_service.revoke_token = AsyncMock(
                side_effect=TokenAlreadyRevoked(token_code=token_code)
            )
            mock_service_class.return_value = mock_service
            
            response = client.post(f"/api/v1/tokens/{token_code}/revoke")
        
        # Assert
        assert response.status_code == 400