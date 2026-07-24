"""Admin Service - User Administration"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.services.password_service import PasswordService
from app.schemas.user import UserResponse
from app.core.exceptions import UserNotFound
from app.utils.logger import logger
from app.models.enums import UserRole
from app.core.audit import (
    audit_admin_user_updated,
    audit_admin_role_changed,
    audit_admin_activate_user,
    audit_admin_deactivate_user,
)


class AdminService:
    """Service for user administration by ADMIN role users.

    Provides user listing, detailed view, field updates,
    activation/deactivation, and role changes.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.password_service = PasswordService()

    async def list_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[UserResponse]:
        """List all users with pagination.

        Args:
            skip: Number of users to skip.
            limit: Maximum users to return.

        Returns:
            list[UserResponse]: List of users.
        """
        users = await self.user_repo.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(u) for u in users]

    async def get_user(self, user_id: str) -> UserResponse:
        """Get a single user by ID.

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
        self, user_id: str, full_name: Optional[str] = None,
        phone: Optional[str] = None,
        admin_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserResponse:
        """Update a user's profile fields.

        Args:
            user_id: The user UUID.
            full_name: Optional new full name.
            phone: Optional new phone number.
            admin_id: The admin user UUID for audit logging.
            ip_address: Optional client IP for audit logging.

        Returns:
            UserResponse: The updated user.

        Raises:
            UserNotFound: If the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        if full_name is not None:
            user.full_name = full_name
        if phone is not None:
            user.phone = phone

        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Admin updated user: user_id={user_id}")
        if admin_id:
            audit_admin_user_updated(
                admin_id=admin_id,
                target_user_id=user_id,
                ip_address=ip_address,
            )

        return UserResponse.model_validate(user)

    async def activate_user(
        self, user_id: str,
        admin_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserResponse:
        """Activate a user account.

        Args:
            user_id: The user UUID.
            admin_id: The admin user UUID for audit logging.
            ip_address: Optional client IP for audit logging.

        Returns:
            UserResponse: The activated user.

        Raises:
            UserNotFound: If the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        user.is_active = True
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Admin activated user: user_id={user_id}")
        if admin_id:
            audit_admin_activate_user(
                admin_id=admin_id,
                target_user_id=user_id,
                ip_address=ip_address,
            )

        return UserResponse.model_validate(user)

    async def deactivate_user(
        self, user_id: str,
        admin_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserResponse:
        """Deactivate a user account.

        Args:
            user_id: The user UUID.
            admin_id: The admin user UUID for audit logging.
            ip_address: Optional client IP for audit logging.

        Returns:
            UserResponse: The deactivated user.

        Raises:
            UserNotFound: If the user does not exist.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        user.is_active = False
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Admin deactivated user: user_id={user_id}")
        if admin_id:
            audit_admin_deactivate_user(
                admin_id=admin_id,
                target_user_id=user_id,
                ip_address=ip_address,
            )

        return UserResponse.model_validate(user)

    async def change_user_role(
        self, user_id: str, role: str,
        admin_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserResponse:
        """Change a user's role.

        Validates the role is one of the known UserRole values.

        Args:
            user_id: The user UUID.
            role: The new role string.
            admin_id: The admin user UUID for audit logging.
            ip_address: Optional client IP for audit logging.

        Returns:
            UserResponse: The updated user.

        Raises:
            UserNotFound: If the user does not exist.
            ValueError: If the role is invalid.
        """
        # Validate role
        valid_roles = [r.value for r in UserRole]
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role '{role}'. Must be one of: {', '.join(valid_roles)}"
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound(user_id=user_id)

        old_role = user.role
        user.role = role
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(
            f"Admin changed user role: user_id={user_id}, "
            f"from={old_role}, to={role}"
        )
        if admin_id:
            audit_admin_role_changed(
                admin_id=admin_id,
                target_user_id=user_id,
                new_role=role,
                ip_address=ip_address,
            )

        return UserResponse.model_validate(user)