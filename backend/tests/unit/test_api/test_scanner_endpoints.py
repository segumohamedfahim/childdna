"""Integration Tests for Scanner API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from fastapi.testclient import TestClient
from main import app
from app.models.enums import TokenStatus
from app.schemas.scanner import ScannerLookupResponse


class TestScannerEndpoints:
    """Test cases for scanner API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_scanner_service(self) -> MagicMock:
        """Mock ScannerService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.scanner.ScannerService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def _make_success_response(self) -> ScannerLookupResponse:
        """Create a mock successful scanner response"""
        return ScannerLookupResponse(
            child_name="John Doe",
            child_age=8,
            child_gender="male",
            guardian_name="Jane Doe",
            guardian_phone="+1234567890",
            token_status=TokenStatus.ACTIVE,
            last_scanned_at=None,
        )

    def test_lookup_success(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test successful scanner lookup"""
        # Arrange
        mock_scanner_service.lookup = AsyncMock(
            return_value=self._make_success_response()
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-ABCD-EFGH"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["child_name"] == "John Doe"
        assert data["child_age"] == 8
        assert data["child_gender"] == "male"
        assert data["guardian_name"] == "Jane Doe"
        assert data["guardian_phone"] == "+1234567890"
        assert data["token_status"] == "active"

    def test_lookup_invalid_format(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup with malformed token code"""
        # Arrange
        from app.core.exceptions import InvalidTokenFormat
        mock_scanner_service.lookup = AsyncMock(
            side_effect=InvalidTokenFormat(token_code="invalid")
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "invalid"},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "INVALID_TOKEN_FORMAT"

    def test_lookup_token_not_found(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup with non-existent token"""
        # Arrange
        from app.core.exceptions import TokenNotFound
        mock_scanner_service.lookup = AsyncMock(
            side_effect=TokenNotFound(token_code="DNA-AAAA-BBBB")
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-AAAA-BBBB"},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "TOKEN_NOT_FOUND"

    def test_lookup_token_not_active(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup with non-active token"""
        # Arrange
        from app.core.exceptions import TokenNotActive
        mock_scanner_service.lookup = AsyncMock(
            side_effect=TokenNotActive(token_code="DNA-ABCD-EFGH")
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-ABCD-EFGH"},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "TOKEN_NOT_ACTIVE"

    def test_lookup_token_revoked(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup with revoked token"""
        # Arrange
        from app.core.exceptions import TokenAlreadyRevoked
        mock_scanner_service.lookup = AsyncMock(
            side_effect=TokenAlreadyRevoked(token_code="DNA-ABCD-EFGH")
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-ABCD-EFGH"},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "TOKEN_ALREADY_REVOKED"

    def test_lookup_token_expired(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup with expired token"""
        # Arrange
        from app.core.exceptions import TokenExpired
        mock_scanner_service.lookup = AsyncMock(
            side_effect=TokenExpired(token_code="DNA-ABCD-EFGH")
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-ABCD-EFGH"},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "TOKEN_EXPIRED"

    def test_lookup_empty_body(
        self,
        client: TestClient,
    ) -> None:
        """Test scanner lookup with empty JSON body"""
        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={},
        )

        # Assert
        assert response.status_code == 422

    def test_lookup_missing_token_code(
        self,
        client: TestClient,
    ) -> None:
        """Test scanner lookup without token_code field"""
        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"other_field": "value"},
        )

        # Assert
        assert response.status_code == 422

    def test_lookup_response_no_ids(
        self,
        client: TestClient,
        mock_scanner_service: MagicMock,
    ) -> None:
        """Test scanner lookup response contains no UUIDs or IDs"""
        # Arrange
        mock_scanner_service.lookup = AsyncMock(
            return_value=self._make_success_response()
        )

        # Act
        response = client.post(
            "/api/v1/scanner/lookup",
            json={"token_code": "DNA-ABCD-EFGH"},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Verify no sensitive fields in response
        assert "qr_secret" not in data
        assert "email" not in data
        assert "address" not in data
        assert "id" not in data
        assert "guardian_id" not in data
        assert "child_id" not in data
        assert "created_at" not in data
        assert "updated_at" not in data
        assert "is_active" not in data