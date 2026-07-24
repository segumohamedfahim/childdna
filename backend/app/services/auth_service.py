"""Auth Service - Authentication and Authorization Logic"""
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from app.core.exceptions import (
    InvalidCredentials,
    InvalidToken,
    UserNotFound,
    UserNotActive,
    EmailAlreadyExists,
    PasswordTooWeak,
    RefreshTokenExpired,
    RefreshTokenRevoked,
)
from app.utils.logger import logger


class AuthService:
    """Service for authentication and user management.

    Handles user registration, login, token refresh, logout,
    password changes, and current user retrieval.
    Uses PasswordService for hashing and JWTService for tokens.
    Refresh tokens are stored as SHA-256 hashes and rotated on use.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
        self.password_service = PasswordService()
        self.jwt_service = JWTService()

    async def register(self, data: UserCreate) -> UserResponse:
        """Register a new user account.

        Validates password strength, checks for duplicate email,
        hashes the password, creates the user, and returns
        the user response (without password hash).

        Args:
            data: User registration data.

        Returns:
            UserResponse: The created user.

        Raises:
            EmailAlreadyExists: If the email is already registered.
            PasswordTooWeak: If the password fails strength checks.
        """
        # Validate password strength
        is_valid, error_msg = self.password_service.validate_password_strength(
            data.password
        )
        if not is_valid:
            raise PasswordTooWeak(message=error_msg)

        # Check for duplicate email
        if await self.user_repo.email_exists(data.email):
            raise EmailAlreadyExists(email=data.email)

        # Hash password
        password_hash = self.password_service.hash_password(data.password)

        # Create user via base repository
        from app.models.user import User
        user = User(
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            phone=data.phone,
            role=data.role,
            guardian_id=data.guardian_id,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            f"User registered: user_id={user.id}, "
            f"email={user.email}, role={user.role}"
        )

        return UserResponse.model_validate(user)

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        """Authenticate a user and return access + refresh tokens.

        Validates email and password, checks user is active,
        updates last_login_at, generates access and refresh tokens,
        stores refresh token hash, and returns the token pair.

        Args:
            data: Login credentials.

        Returns:
            TokenResponse: Access token, refresh token, and metadata.

        Raises:
            InvalidCredentials: If email or password is wrong.
            UserNotActive: If the user account is inactive.
        """
        # Find user by email
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise InvalidCredentials()

        # Verify password
        if not self.password_service.verify_password(
            data.password, user.password_hash
        ):
            raise InvalidCredentials()

        # Check user is active
        if not user.is_active:
            raise UserNotActive(user_id=str(user.id))

        # Update last login
        await self.user_repo.update_last_login(str(user.id))

        # Generate tokens
        access_token = self.jwt_service.create_access_token(
            user_id=str(user.id),
            role=user.role,
            additional_claims={"guardian_id": str(user.guardian_id) if user.guardian_id else None},
        )

        refresh_token_str, token_hash = self._generate_refresh_token_pair()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=30  # Fixed 30-day refresh token lifetime
        )

        # Store refresh token hash
        from app.models.refresh_token import RefreshToken
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_token_record)
        await self.session.commit()

        logger.info(
            f"User logged in: user_id={user.id}, email={user.email}"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=self.jwt_service.access_token_expire_minutes * 60,
        )

    async def refresh_token(self, data: RefreshTokenRequest) -> TokenResponse:
        """Refresh an access token using a refresh token.

        Validates the refresh token hash, checks expiry and revocation,
        rotates the refresh token (issues new, revokes old),
        and returns a new access + refresh token pair.

        Args:
            data: Refresh token request.

        Returns:
            TokenResponse: New access token, refresh token, and metadata.

        Raises:
            InvalidToken: If the refresh token is not found.
            RefreshTokenExpired: If the refresh token has expired.
            RefreshTokenRevoked: If the refresh token has been revoked.
        """
        # Hash the provided refresh token
        token_hash = self._hash_token(data.refresh_token)

        # Find stored token
        stored_token = await self.token_repo.get_by_token_hash(token_hash)
        if not stored_token:
            raise InvalidToken(message="Refresh token not found")

        # Check expiry
        if stored_token.expires_at < datetime.now(timezone.utc):
            raise RefreshTokenExpired()

        # Check revocation
        if stored_token.revoked:
            raise RefreshTokenRevoked()

        # Revoke old token (rotation)
        await self.token_repo.revoke(token_hash)

        # Get user
        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user:
            raise InvalidToken(message="User not found for refresh token")

        if not user.is_active:
            raise UserNotActive(user_id=str(user.id))

        # Generate new tokens
        access_token = self.jwt_service.create_access_token(
            user_id=str(user.id),
            role=user.role,
            additional_claims={"guardian_id": str(user.guardian_id) if user.guardian_id else None},
        )

        new_refresh_token_str, new_token_hash = self._generate_refresh_token_pair()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        # Store new refresh token
        from app.models.refresh_token import RefreshToken
        new_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=expires_at,
        )
        self.session.add(new_record)
        await self.session.commit()

        logger.info(
            f"Token refreshed: user_id={user.id}"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token_str,
            token_type="bearer",
            expires_in=self.jwt_service.access_token_expire_minutes * 60,
        )

    async def logout(self, user_id: str, refresh_token: str) -> None:
        """Logout by revoking the specific refresh token.

        Args:
            user_id: The user UUID (for audit).
            refresh_token: The refresh token string to revoke.
        """
        token_hash = self._hash_token(refresh_token)
        stored = await self.token_repo.get_by_token_hash(token_hash)

        if stored:
            # Only revoke if it belongs to the requesting user
            if str(stored.user_id) == user_id:
                await self.token_repo.revoke(token_hash)
                logger.info(
                    f"User logged out: user_id={user_id}, "
                    f"token_revoked=True"
                )

    async def logout_all(self, user_id: str) -> int:
        """Logout from all sessions by revoking all refresh tokens.

        Args:
            user_id: The user UUID.

        Returns:
            int: Number of tokens revoked.
        """
        count = await self.token_repo.revoke_all_for_user(user_id)
        logger.info(
            f"User logged out from all sessions: "
            f"user_id={user_id}, tokens_revoked={count}"
        )
        return count

    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get the current user by ID.

        Args:
            user_id: The user UUID.

        Returns:
            UserResponse: The user.

        Raises:
            UserNotFound: If the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)
        return UserResponse.model_validate(user)

    async def update_user(
        self, user_id: str, data: UserUpdate
    ) -> UserResponse:
        """Update a user's profile.

        Args:
            user_id: The user UUID.
            data: Fields to update.

        Returns:
            UserResponse: The updated user.

        Raises:
            UserNotFound: If the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        user = await self.user_repo.update(user, data)
        return UserResponse.model_validate(user)

    async def change_password(
        self, user_id: str, data: ChangePasswordRequest
    ) -> None:
        """Change a user's password.

        Verifies the current password, validates the new password
        strength, and updates the password hash.

        Args:
            user_id: The user UUID.
            data: Current and new password.

        Raises:
            UserNotFound: If the user does not exist.
            InvalidCredentials: If the current password is wrong.
            PasswordTooWeak: If the new password fails strength checks.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        # Verify current password
        if not self.password_service.verify_password(
            data.current_password, user.password_hash
        ):
            raise InvalidCredentials()

        # Validate new password strength
        is_valid, error_msg = self.password_service.validate_password_strength(
            data.new_password
        )
        if not is_valid:
            raise PasswordTooWeak(message=error_msg)

        # Hash and update
        new_hash = self.password_service.hash_password(data.new_password)
        user.password_hash = new_hash
        await self.session.commit()

        logger.info(
            f"Password changed: user_id={user_id}"
        )

    def _generate_refresh_token_pair(self) -> tuple[str, str]:
        """Generate a cryptographically secure refresh token and its hash.

        Returns:
            tuple[str, str]: (raw_token, sha256_hash).
        """
        raw_token = secrets.token_urlsafe(48)
        token_hash = self._hash_token(raw_token)
        return raw_token, token_hash

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token string using SHA-256.

        Args:
            token: The raw token string.

        Returns:
            str: The SHA-256 hex digest.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()