"""Guardian Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.guardian import Guardian
from app.schemas.guardian import GuardianCreate, GuardianUpdate
from app.repositories.base import BaseRepository


class GuardianRepository(BaseRepository[Guardian]):
    """Repository for Guardian entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Guardian)
    
    async def get_by_email(self, email: str) -> Optional[Guardian]:
        """Get guardian by email"""
        result = await self.session.execute(
            select(Guardian).where(Guardian.email == email)
        )
        return result.scalar_one_or_none()
    
    async def delete(self, guardian: Guardian) -> None:
        """Soft delete a guardian"""
        guardian.is_active = False
        await self.session.commit()
