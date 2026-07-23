"""Scanner Service - Token Lookup Business Logic"""
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.child import Child
from app.models.guardian import Guardian
from app.models.child_token import ChildToken
from app.models.enums import TokenStatus
from app.repositories.child_token import ChildTokenRepository
from app.schemas.scanner import ScannerLookupRequest, ScannerLookupResponse
from app.core.exceptions import (
    TokenNotFound,
    TokenNotActive,
    TokenAlreadyRevoked,
    TokenExpired,
    InvalidTokenFormat,
)
from app.utils.token_generator import validate_format
from app.utils.logger import logger


class ScannerService:
    """Service for QR scanner token lookup operations.

    Validates the token, loads child and guardian data, records
    the scan timestamp, and returns only safe public information.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ChildTokenRepository(session)

    async def lookup(
        self, request: ScannerLookupRequest
    ) -> ScannerLookupResponse:
        """Perform a token lookup from a QR scanner.

        Validates the token, enforces lifecycle constraints, loads
        associated child and guardian data, records the scan, and
        returns only safe public rescue information.

        Args:
            request: Scanner lookup request containing the token code.

        Returns:
            ScannerLookupResponse: Public rescue information.

        Raises:
            InvalidTokenFormat: If the token code format is invalid.
            TokenNotFound: If the token does not exist.
            TokenNotActive: If the token status is not ACTIVE.
            TokenAlreadyRevoked: If the token has been revoked.
            TokenExpired: If the token has expired.
        """
        token_code = request.token_code

        # Validate token format
        if not validate_format(token_code):
            logger.warning(
                f"Scanner lookup failed - invalid format: token_code={token_code}"
            )
            raise InvalidTokenFormat(token_code=token_code)

        # Fetch token
        token = await self.repository.get_by_token_code(token_code)
        if not token:
            logger.warning(
                f"Scanner lookup failed - not found: token_code={token_code}"
            )
            raise TokenNotFound(token_code=token_code)

        # Validate token lifecycle status
        self._validate_token_status(token)

        # Load child and guardian via ORM relationships (lazy="selectin")
        child = token.child
        guardian = child.guardian

        # Record the scan
        token = await self.repository.record_scan(token)

        logger.info(
            f"Scanner lookup success: token_code={token_code}, "
            f"child_name={child.full_name}"
        )

        return self._build_response(token, child, guardian)

    def _validate_token_status(self, token: ChildToken) -> None:
        """Validate that the token is in a scannable state.

        Args:
            token: The child token model instance.

        Raises:
            TokenAlreadyRevoked: If token is revoked.
            TokenExpired: If token is expired.
            TokenNotActive: If token is not ACTIVE.
        """
        if token.status == TokenStatus.REVOKED:
            logger.warning(
                f"Scanner lookup failed - revoked: "
                f"token_code={token.token_code}"
            )
            raise TokenAlreadyRevoked(token_code=token.token_code)

        if token.status == TokenStatus.EXPIRED:
            logger.warning(
                f"Scanner lookup failed - expired: "
                f"token_code={token.token_code}"
            )
            raise TokenExpired(token_code=token.token_code)

        if token.status != TokenStatus.ACTIVE:
            logger.warning(
                f"Scanner lookup failed - not active: "
                f"token_code={token.token_code}, "
                f"status={token.status}"
            )
            raise TokenNotActive(token_code=token.token_code)

    def _build_response(
        self,
        token: ChildToken,
        child: Child,
        guardian: Guardian,
    ) -> ScannerLookupResponse:
        """Build the safe public response from domain models.

        Args:
            token: The updated child token.
            child: The associated child entity.
            guardian: The associated guardian entity.

        Returns:
            ScannerLookupResponse: Safe public rescue information.
        """
        return ScannerLookupResponse(
            child_name=child.full_name,
            child_age=self._compute_age(child.date_of_birth),
            child_gender=child.gender,
            guardian_name=guardian.full_name,
            guardian_phone=guardian.phone,
            token_status=token.status,
            last_scanned_at=token.last_scanned_at,
        )

    def _compute_age(self, date_of_birth: date) -> int:
        """Compute child's age in years from date of birth.

        Args:
            date_of_birth: The child's birth date.

        Returns:
            int: Age in whole years.
        """
        today = datetime.now(timezone.utc).date()
        return (
            today.year
            - date_of_birth.year
            - (
                (today.month, today.day)
                < (date_of_birth.month, date_of_birth.day)
            )
        )