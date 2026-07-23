"""Unit Tests for QR Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import anyio
import segno
from app.services.qr_service import QRService, QRResult
from app.models.enums import TokenStatus
from app.core.exceptions import (
    TokenNotFound,
    TokenNotActiveForQR,
    TokenAlreadyRevoked,
    TokenExpired,
    InvalidTokenFormat,
)
from app.utils.qr_generator import _build_payload


class TestQRService:
    """Test cases for QRService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def qr_service(self, mock_session: AsyncMock) -> QRService:
        """Create QRService with mock session"""
        return QRService(mock_session)

    @pytest.fixture
    def mock_token_repository(self, qr_service: QRService) -> MagicMock:
        """Mock token repository"""
        return qr_service.repository

    def _make_mock_token(
        self,
        token_code: str = "DNA-ABCD-EFGH",
        status: TokenStatus = TokenStatus.ACTIVE,
    ) -> MagicMock:
        """Create a mock token with given attributes"""
        token = MagicMock()
        token.token_code = token_code
        token.status = status
        token.child_id = "child-id"
        token.qr_secret = "test-secret"
        return token

    def test_generate_qr_svg_active_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with active token in SVG format"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await qr_service.generate_qr(
                token_code=token_code,
                format="svg",
                size=300,
            )

            # Assert
            assert isinstance(result, QRResult)
            assert result.media_type == "image/svg+xml"
            assert result.filename == "DNA-ABCD-EFGH.svg"
            assert isinstance(result.content, bytes)
            assert len(result.content) > 0
            assert b"<svg" in result.content
            mock_token_repository.get_by_token_code.assert_called_once_with(
                token_code
            )

        anyio.run(run_test)

    def test_generate_qr_png_active_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with active token in PNG format"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await qr_service.generate_qr(
                token_code=token_code,
                format="png",
                size=300,
            )

            # Assert
            assert isinstance(result, QRResult)
            assert result.media_type == "image/png"
            assert result.filename == "DNA-ABCD-EFGH.png"
            assert isinstance(result.content, bytes)
            assert len(result.content) > 0
            # PNG header bytes (requires Pillow for generation)
            assert result.content[:4] == b"\x89PNG"

        anyio.run(run_test)

    def test_generate_qr_issued_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with issued (not yet active) token"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.ISSUED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await qr_service.generate_qr(
                token_code=token_code,
                format="svg",
            )

            # Assert
            assert isinstance(result, QRResult)
            assert result.media_type == "image/svg+xml"

        anyio.run(run_test)

    def test_generate_qr_token_not_found(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with non-existent token"""
        async def run_test():
            # Arrange
            # Must use a valid format token; the service validates format first
            token_code = "DNA-AAAA-BBBB"
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=None
            )

            # Act & Assert
            with pytest.raises(TokenNotFound):
                await qr_service.generate_qr(token_code=token_code)

        anyio.run(run_test)

    def test_generate_qr_revoked_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with revoked token"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.REVOKED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenAlreadyRevoked):
                await qr_service.generate_qr(token_code=token_code)

        anyio.run(run_test)

    def test_generate_qr_expired_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with expired token"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.EXPIRED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenExpired):
                await qr_service.generate_qr(token_code=token_code)

        anyio.run(run_test)

    def test_generate_qr_used_token(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with used token (not allowed)"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.USED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenNotActiveForQR):
                await qr_service.generate_qr(token_code=token_code)

        anyio.run(run_test)

    def test_generate_qr_invalid_format(
        self,
        qr_service: QRService,
    ) -> None:
        """Test QR generation with malformed token code"""
        async def run_test():
            # Act & Assert
            with pytest.raises(InvalidTokenFormat):
                await qr_service.generate_qr(token_code="invalid-token")

        anyio.run(run_test)

    def test_generate_qr_custom_size(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR generation with custom size"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await qr_service.generate_qr(
                token_code=token_code,
                format="svg",
                size=500,
            )

            # Assert
            assert isinstance(result, QRResult)
            assert len(result.content) > 0

        anyio.run(run_test)

    def test_generate_qr_payload_correct(
        self,
        qr_service: QRService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test QR encodes the correct payload with childdna: prefix"""
        async def run_test():
            # Arrange
            token_code = "DNA-ABCD-EFGH"
            mock_token = self._make_mock_token(
                token_code=token_code,
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await qr_service.generate_qr(
                token_code=token_code,
                format="svg",
            )

            # Assert: Verify payload builder produces correct string
            expected_payload = _build_payload(token_code)
            assert expected_payload == "childdna:DNA-ABCD-EFGH"
            assert isinstance(result, QRResult)
            assert len(result.content) > 0

        anyio.run(run_test)
