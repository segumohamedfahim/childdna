"""User Repository - Data Access Layer for Users"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address.

        Args:
            email: The email address to look up.

        Returns:
            Optional[User]: The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_guardian_id(self, guardian_id: str) -> Optional[User]:
        """Find a user linked to a guardian record.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            Optional[User]: The user if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.guardian_id == guardian_id)
        )
        return result.scalar_one_or_none()

    async def update_last_login(self, user_id: str) -> None:
        """Update the last_login_at timestamp for a user.

        Args:
            user_id: The user UUID.
        """
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await self.session.commit()

    async def verify_email(self, user_id: str) -> Optional[User]:
        """Mark a user's email as verified.

        Args:
            user_id: The user UUID.

        Returns:
            Optional[User]: The updated user if found, None otherwise.
        """
        user = await self.get_by_id(user_id)
        if user:
            user.email_verified = True
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered.

        Args:
            email: The email address to check.

        Returns:
            bool: True if the email exists.
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None