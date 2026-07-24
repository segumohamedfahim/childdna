"""Authentication Dependencies - JWT Token Validation"""
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt as pyjwt
from app.database.connection import get_db
from app.repositories.user import UserRepository
from app.models.user import User
from app.core.exceptions import InvalidToken, ExpiredToken
from app.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT, return authenticated User.

    Decodes the Bearer token from the Authorization header,
    extracts the user_id from the 'sub' claim, looks up the
    user in the database, and returns the User model.

    Args:
        token: The JWT access token from the Authorization header.
        session: Database session.

    Returns:
        User: The authenticated user.

    Raises:
        InvalidToken: If the token is missing, malformed, or invalid.
        ExpiredToken: If the token has expired.
    """
    if token is None:
        raise InvalidToken(message="Authentication required")

    try:
        payload = pyjwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except pyjwt.ExpiredSignatureError:
        raise ExpiredToken()
    except pyjwt.InvalidTokenError:
        raise InvalidToken(message="Invalid authentication token")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise InvalidToken(message="Invalid token payload")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise InvalidToken(message="User not found for token")

    return user


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Return authenticated user if token present, None otherwise.

    Unlike get_current_user, this dependency does not raise an
    exception when no token is provided. This allows endpoints
    to work for both authenticated and unauthenticated users.

    Args:
        token: The JWT access token (optional).
        session: Database session.

    Returns:
        Optional[User]: The authenticated user, or None.
    """
    if token is None:
        return None

    try:
        payload = pyjwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError):
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    repo = UserRepository(session)
    return await repo.get_by_id(user_id)