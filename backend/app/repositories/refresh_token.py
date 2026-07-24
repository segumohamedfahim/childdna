"""RefreshToken Repository - Data Access Layer for Refresh Tokens"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshToken)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Find a refresh token by its SHA-256 hash.

        Args:
            token_hash: The SHA-256 hash of the refresh token.

        Returns:
            Optional[RefreshToken]: The token record if found, None otherwise.
        """
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: str) -> list[RefreshToken]:
        """Get all non-revoked, non-expired tokens for a user.

        Args:
            user_id: The user UUID.

        Returns:
            list[RefreshToken]: Active tokens for the user.
        """
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now,
            )
            .order_by(RefreshToken.created_at.desc())
        )
        return result.scalars().all()

    async def revoke(self, token_hash: str) -> Optional[RefreshToken]:
        """Revoke a specific refresh token.

        Args:
            token_hash: The SHA-256 hash of the token to revoke.

        Returns:
            Optional[RefreshToken]: The revoked token if found, None otherwise.
        """
        token = await self.get_by_token_hash(token_hash)
        if token:
            token.revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(token)
        return token

    async def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all active refresh tokens for a user.

        Args:
            user_id: The user UUID.

        Returns:
            int: Number of tokens revoked.
        """
        now = datetime.now(timezone.utc)
        tokens = await self.get_active_by_user(user_id)
        count = 0
        for token in tokens:
            token.revoked = True
            token.revoked_at = now
            count += 1
        if count > 0:
            await self.session.commit()
        return count

    async def cleanup_expired(self) -> int:
        """Delete all expired refresh tokens.

        Returns:
            int: Number of tokens deleted.
        """
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at <= now)
        )
        await self.session.commit()
        return result.rowcount