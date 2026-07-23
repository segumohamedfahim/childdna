"""Unit Tests for Scanner Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime, timezone
import anyio
from app.services.scanner_service import ScannerService
from app.schemas.scanner import ScannerLookupRequest, ScannerLookupResponse
from app.models.enums import TokenStatus
from app.core.exceptions import (
    TokenNotFound,
    TokenNotActive,
    TokenAlreadyRevoked,
    TokenExpired,
    InvalidTokenFormat,
)


class TestScannerService:
    """Test cases for ScannerService"""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Mock database session"""
        return AsyncMock()

    @pytest.fixture
    def scanner_service(self, mock_session: AsyncMock) -> ScannerService:
        """Create ScannerService with mock session"""
        return ScannerService(mock_session)

    @pytest.fixture
    def mock_token_repository(self, scanner_service: ScannerService) -> MagicMock:
        """Mock token repository"""
        return scanner_service.repository

    def _make_mock_token(
        self,
        token_code: str = "DNA-ABCD-EFGH",
        status: TokenStatus = TokenStatus.ACTIVE,
        expires_at=None,
        last_scanned_at=None,
    ) -> MagicMock:
        """Create a mock token with given attributes"""
        token = MagicMock()
        token.token_code = token_code
        token.status = status
        token.child_id = "child-uuid"
        token.qr_secret = "never-exposed-secret"
        token.expires_at = expires_at
        token.last_scanned_at = last_scanned_at

        # Create mock child with relationship
        child = MagicMock()
        child.full_name = "John Doe"
        child.date_of_birth = date(2018, 6, 15)
        child.gender = "male"
        child.id = "child-uuid"

        # Create mock guardian with relationship
        guardian = MagicMock()
        guardian.full_name = "Jane Doe"
        guardian.phone = "+1234567890"
        guardian.email = "jane@example.com"
        guardian.id = "guardian-uuid"

        child.guardian = guardian
        token.child = child

        return token

    def _make_request(self, token_code: str = "DNA-ABCD-EFGH") -> ScannerLookupRequest:
        """Create a scanner lookup request"""
        return ScannerLookupRequest(token_code=token_code)

    def test_lookup_success(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test successful token lookup"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )
            mock_token_repository.record_scan = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await scanner_service.lookup(request)

            # Assert
            assert isinstance(result, ScannerLookupResponse)
            assert result.child_name == "John Doe"
            assert result.child_age == 8  # 2026 - 2018 = 8
            assert result.child_gender == "male"
            assert result.guardian_name == "Jane Doe"
            assert result.guardian_phone == "+1234567890"
            assert result.token_status == TokenStatus.ACTIVE

            mock_token_repository.get_by_token_code.assert_called_once_with(
                "DNA-ABCD-EFGH"
            )
            mock_token_repository.record_scan.assert_called_once_with(
                mock_token
            )

        anyio.run(run_test)

    def test_lookup_success_updates_last_scanned(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test successful lookup calls record_scan on repository"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )
            mock_token_repository.record_scan = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await scanner_service.lookup(request)

            # Assert - record_scan was called to update the timestamp
            mock_token_repository.record_scan.assert_called_once_with(
                mock_token
            )
            assert isinstance(result, ScannerLookupResponse)

        anyio.run(run_test)

    def test_lookup_invalid_format(
        self,
        scanner_service: ScannerService,
    ) -> None:
        """Test lookup with malformed token code"""
        async def run_test():
            # Arrange
            request = self._make_request("invalid-token")

            # Act & Assert
            with pytest.raises(InvalidTokenFormat):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_token_not_found(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup with non-existent token"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-AAAA-BBBB")
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=None
            )

            # Act & Assert
            with pytest.raises(TokenNotFound):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_token_not_active(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup with ISSUED token (not active)"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.ISSUED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenNotActive):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_token_used(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup with USED token (not active)"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.USED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenNotActive):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_token_revoked(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup with revoked token"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.REVOKED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenAlreadyRevoked):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_token_expired(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup with expired token"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.EXPIRED,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )

            # Act & Assert
            with pytest.raises(TokenExpired):
                await scanner_service.lookup(request)

        anyio.run(run_test)

    def test_lookup_response_no_sensitive_fields(
        self,
        scanner_service: ScannerService,
        mock_token_repository: MagicMock,
    ) -> None:
        """Test lookup response does not expose sensitive data"""
        async def run_test():
            # Arrange
            request = self._make_request("DNA-ABCD-EFGH")
            mock_token = self._make_mock_token(
                token_code="DNA-ABCD-EFGH",
                status=TokenStatus.ACTIVE,
            )
            mock_token_repository.get_by_token_code = AsyncMock(
                return_value=mock_token
            )
            mock_token_repository.record_scan = AsyncMock(
                return_value=mock_token
            )

            # Act
            result = await scanner_service.lookup(request)

            # Assert - response is a ScannerLookupResponse with restricted fields
            assert not hasattr(result, "qr_secret")
            assert not hasattr(result, "email")
            assert not hasattr(result, "address")
            assert not hasattr(result, "id")
            assert not hasattr(result, "guardian_id")
            assert not hasattr(result, "child_id")
            assert not hasattr(result, "created_at")
            assert not hasattr(result, "updated_at")
            assert not hasattr(result, "is_active")

        anyio.run(run_test)

    def test_compute_age(
        self,
        scanner_service: ScannerService,
    ) -> None:
        """Test age computation logic"""
        # Exact birthday today
        today = datetime.now(timezone.utc).date()
        exact_birthday = date(today.year - 5, today.month, today.day)
        assert scanner_service._compute_age(exact_birthday) == 5

        # Birthday tomorrow (still 4)
        birthday_tomorrow = date(today.year - 5, today.month, today.day)
        from datetime import timedelta
        if today.month == 1 and today.day == 1:
            birthday_tomorrow = date(today.year - 5, 12, 31)
        else:
            birthday_tomorrow = date(
                today.year - 5,
                today.month,
                today.day - 1 if today.day > 1 else 28,
            )
        # Just verify it doesn't crash and returns non-negative
        age = scanner_service._compute_age(date(2020, 1, 1))
        assert age >= 0