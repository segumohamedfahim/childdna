"""Integration Tests for QR Code API Endpoints"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.models.enums import TokenStatus
from app.services.qr_service import QRResult


class TestQREndpoints:
    """Test cases for QR code API endpoints"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Test client fixture"""
        return TestClient(app)

    @pytest.fixture
    def mock_qr_service(self) -> MagicMock:
        """Mock QRService for endpoint testing"""
        with patch(
            "app.api.v1.endpoints.qr_code.QRService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            yield mock_service

    def _make_svg_result(self) -> QRResult:
        """Create a mock SVG QR result"""
        return QRResult(
            content=b'<svg xmlns="http://www.w3.org/2000/svg">test</svg>',
            media_type="image/svg+xml",
            filename="DNA-ABCD-EFGH.svg",
        )

    def _make_png_result(self) -> QRResult:
        """Create a mock PNG QR result"""
        return QRResult(
            content=b"\x89PNG\r\n\x1a\n" + b"\x00" * 100,
            media_type="image/png",
            filename="DNA-ABCD-EFGH.png",
        )

    def test_get_qr_svg_default(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with default SVG format"""
        # Arrange
        mock_qr_service.generate_qr = AsyncMock(
            return_value=self._make_svg_result()
        )

        # Act
        response = client.get("/api/v1/tokens/DNA-ABCD-EFGH/qr")

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"
        assert b"<svg" in response.content

    def test_get_qr_png_format(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with PNG format"""
        # Arrange
        mock_qr_service.generate_qr = AsyncMock(
            return_value=self._make_png_result()
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?format=png"
        )

        # Assert
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_get_qr_download_svg(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with download=true (SVG)"""
        # Arrange
        mock_qr_service.generate_qr = AsyncMock(
            return_value=self._make_svg_result()
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?download=true"
        )

        # Assert
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "DNA-ABCD-EFGH.svg" in response.headers["content-disposition"]

    def test_get_qr_download_png(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with download=true (PNG)"""
        # Arrange
        mock_qr_service.generate_qr = AsyncMock(
            return_value=self._make_png_result()
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?format=png&download=true"
        )

        # Assert
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "DNA-ABCD-EFGH.png" in response.headers["content-disposition"]

    def test_get_qr_custom_size(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with custom size"""
        # Arrange
        mock_qr_service.generate_qr = AsyncMock(
            return_value=self._make_svg_result()
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?size=500"
        )

        # Assert
        assert response.status_code == 200
        # Verify the service was called with size=500
        mock_qr_service.generate_qr.assert_called_once()
        call_kwargs = mock_qr_service.generate_qr.call_args[1]
        assert call_kwargs["size"] == 500

    def test_get_qr_invalid_format(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with invalid format parameter"""
        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?format=jpg"
        )

        # Assert
        assert response.status_code == 422

    def test_get_qr_size_too_small(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with size below minimum"""
        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?size=10"
        )

        # Assert
        assert response.status_code == 422

    def test_get_qr_size_too_large(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with size above maximum"""
        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr?size=5000"
        )

        # Assert
        assert response.status_code == 422

    def test_get_qr_token_not_found(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with non-existent token"""
        # Arrange
        from app.core.exceptions import TokenNotFound
        mock_qr_service.generate_qr = AsyncMock(
            side_effect=TokenNotFound(token_code="DNA-NONEXISTENT")
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-NONEXISTENT/qr"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "TOKEN_NOT_FOUND"

    def test_get_qr_revoked_token(
        self,
        client: TestClient,
        mock_qr_service: MagicMock,
    ) -> None:
        """Test QR endpoint with revoked token"""
        # Arrange
        from app.core.exceptions import TokenAlreadyRevoked
        mock_qr_service.generate_qr = AsyncMock(
            side_effect=TokenAlreadyRevoked(token_code="DNA-ABCD-EFGH")
        )

        # Act
        response = client.get(
            "/api/v1/tokens/DNA-ABCD-EFGH/qr"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "TOKEN_ALREADY_REVOKED"