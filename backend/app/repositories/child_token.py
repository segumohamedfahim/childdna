"""ChildToken Repository - Data Access Layer"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.child_token import ChildToken
from app.schemas.child_token import ChildTokenCreate, ChildTokenUpdate
from app.repositories.base import BaseRepository
from app.models.enums import TokenStatus


class ChildTokenRepository(BaseRepository[ChildToken]):
    """Repository for ChildToken entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChildToken)
    
    async def get_by_token_code(self, token_code: str) -> Optional[ChildToken]:
        """Get token by token code"""
        result = await self.session.execute(
            select(ChildToken).where(ChildToken.token_code == token_code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_child(self, child_id: str) -> list[ChildToken]:
        """Get all tokens for a child"""
        result = await self.session.execute(
            select(ChildToken).where(ChildToken.child_id == child_id)
        )
        return result.scalars().all()
    
    async def token_exists(self, token_code: str) -> bool:
        """Check if a token code already exists"""
        result = await self.session.execute(
            select(ChildToken).where(ChildToken.token_code == token_code)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_active_by_child(self, child_id: str) -> Optional[ChildToken]:
        """Get active token for a child"""
        result = await self.session.execute(
            select(ChildToken).where(
                ChildToken.child_id == child_id,
                ChildToken.status == TokenStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()
    
    async def activate(self, token: ChildToken) -> ChildToken:
        """Set token status to active"""
        token.status = TokenStatus.ACTIVE
        await self.session.commit()
        await self.session.refresh(token)
        return token
    
    async def revoke(self, token: ChildToken) -> ChildToken:
        """Set token status to revoked"""
        token.status = TokenStatus.REVOKED
        token.revoked_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(token)
        return token
    
    async def expire(self, token: ChildToken) -> ChildToken:
        """Set token status to expired"""
        token.status = TokenStatus.EXPIRED
        await self.session.commit()
        await self.session.refresh(token)
        return token
    
    async def record_scan(self, token: ChildToken) -> ChildToken:
        """Update last_scanned_at timestamp after a successful scan.

        Args:
            token: The child token model instance.

        Returns:
            ChildToken: The updated token with refreshed attributes.
        """
        token.last_scanned_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def delete(self, token: ChildToken) -> None:
        """Soft delete a token"""
        token.is_active = False
        await self.session.commit()
