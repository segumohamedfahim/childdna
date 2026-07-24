"""Authentication Dependencies - JWT Token Validation and RBAC"""
from typing import Optional, Callable
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt as pyjwt
from app.database.connection import get_db
from app.repositories.user import UserRepository
from app.models.user import User
from app.models.enums import UserRole
from app.core.exceptions import InvalidToken, ExpiredToken, InsufficientPermissions
from app.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT, return authenticated User."""
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
    """Return authenticated user if token present, None otherwise."""
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


def require_role(*roles: UserRole) -> Callable:
    """Return a dependency that checks the user has one of the given roles.

    Usage:
        @router.get("/admin/users")
        async def list_users(
            current_user: User = Depends(require_role(UserRole.ADMIN)),
        ):
            ...

    The role check is delegated to _verify_role which can be overridden
    in tests via dependency_overrides.
    """
    async def _role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in [r.value for r in roles]:
            raise InsufficientPermissions(
                required_roles=[r.value for r in roles]
            )
        return current_user

    return _role_checker