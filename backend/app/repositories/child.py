"""Child Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.child import Child
from app.schemas.child import ChildCreate, ChildUpdate
from app.repositories.base import BaseRepository


class ChildRepository(BaseRepository[Child]):
    """Repository for Child entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Child)
    
    async def get_by_guardian(self, guardian_id: str) -> list[Child]:
        """Get all children for a guardian"""
        result = await self.session.execute(
            select(Child).where(Child.guardian_id == guardian_id)
        )
        return result.scalars().all()
