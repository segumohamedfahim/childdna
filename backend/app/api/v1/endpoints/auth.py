"""Authentication API Endpoints - Register, Login, Refresh, Logout"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.api.dependencies.auth import get_current_user
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from app.models.user import User

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account with email, password, and profile "
        "information. Validates password strength and checks for "
        "duplicate emails."
    ),
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account.

    Args:
        user_data: User registration data.
        session: Database session.

    Returns:
        UserResponse: The created user.
    """
    service = AuthService(session)
    return await service.register(user_data)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and get access tokens",
    description=(
        "Authenticates a user with email and password. Returns "
        "an access token (short-lived) and a refresh token "
        "(long-lived) for session management."
    ),
)
async def login(
    login_data: UserLoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return tokens.

    Args:
        login_data: Login credentials.
        session: Database session.

    Returns:
        TokenResponse: Access and refresh tokens.
    """
    service = AuthService(session)
    return await service.login(login_data)


@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Exchanges a valid refresh token for a new access token "
        "and refresh token pair. Implements token rotation: the "
        "old refresh token is revoked."
    ),
)
async def refresh(
    refresh_data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh an access token using a refresh token.

    Args:
        refresh_data: Refresh token request.
        session: Database session.

    Returns:
        TokenResponse: New access and refresh tokens.
    """
    service = AuthService(session)
    return await service.refresh_token(refresh_data)


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke refresh token",
    description=(
        "Revokes the provided refresh token, effectively logging "
        "out the current session. Requires authentication."
    ),
)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Logout by revoking the refresh token.

    Args:
        refresh_data: Refresh token to revoke.
        current_user: The authenticated user.
        session: Database session.
    """
    service = AuthService(session)
    await service.logout(str(current_user.id), refresh_data.refresh_token)


@router.post(
    "/auth/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Logout from all sessions",
    description=(
        "Revokes all active refresh tokens for the authenticated "
        "user, logging them out from all devices."
    ),
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Logout from all sessions.

    Args:
        current_user: The authenticated user.
        session: Database session.

    Returns:
        dict: Number of tokens revoked.
    """
    service = AuthService(session)
    count = await service.logout_all(str(current_user.id))
    return {"revoked": count}


@router.get(
    "/auth/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Returns the authenticated user's profile information. "
        "Requires a valid access token."
    ),
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get the current user's profile.

    Args:
        current_user: The authenticated user.

    Returns:
        UserResponse: The user profile.
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/auth/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Updates the authenticated user's profile fields "
        "(full_name, phone, email). Requires a valid access token."
    ),
)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update the current user's profile.

    Args:
        update_data: Fields to update.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        UserResponse: The updated user profile.
    """
    service = AuthService(session)
    return await service.update_user(str(current_user.id), update_data)


@router.post(
    "/auth/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description=(
        "Changes the authenticated user's password. Requires "
        "the current password for verification and validates "
        "the new password strength."
    ),
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Change the current user's password.

    Args:
        password_data: Current and new password.
        current_user: The authenticated user.
        session: Database session.
    """
    service = AuthService(session)
    await service.change_password(str(current_user.id), password_data)