"""Admin API Endpoints - User Administration"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.admin_service import AdminService
from app.schemas.user import UserResponse
from app.api.dependencies.auth import require_role
from app.models.enums import UserRole

router = APIRouter(tags=["admin"])


@router.get(
    "/admin/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description=(
        "Returns a paginated list of all registered users. "
        "Only accessible by ADMIN role."
    ),
)
async def list_users(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=200, description="Max records"),
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> list[UserResponse]:
    """List all users with pagination."""
    service = AdminService(session)
    return await service.list_users(skip=skip, limit=limit)


@router.get(
    "/admin/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieves a single user by their UUID. Admin only.",
)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Get a single user by ID."""
    service = AdminService(session)
    return await service.get_user(user_id)


@router.patch(
    "/admin/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    description="Updates a user's full_name and/or phone. Admin only.",
)
async def update_user(
    user_id: str,
    full_name: str | None = Query(None, description="New full name"),
    phone: str | None = Query(None, description="New phone number"),
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Update a user's profile fields."""
    service = AdminService(session)
    return await service.update_user(
        user_id=user_id, full_name=full_name, phone=phone,
    )


@router.post(
    "/admin/users/{user_id}/activate",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a user",
    description="Activates a user account. Admin only.",
)
async def activate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Activate a user account."""
    service = AdminService(session)
    return await service.activate_user(user_id)


@router.post(
    "/admin/users/{user_id}/deactivate",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate a user",
    description="Deactivates a user account. Admin only.",
)
async def deactivate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Deactivate a user account."""
    service = AdminService(session)
    return await service.deactivate_user(user_id)


@router.post(
    "/admin/users/{user_id}/change-role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user role",
    description="Changes a user's role. Admin only.",
)
async def change_user_role(
    user_id: str,
    role: str = Query(..., description="New role (guardian, authority, admin, scanner)"),
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """Change a user's role."""
    service = AdminService(session)
    try:
        return await service.change_user_role(user_id=user_id, role=role)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))