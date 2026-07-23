"""RescueSession Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rescue_session import RescueSession
from app.schemas.rescue_session import RescueSessionCreate, RescueSessionUpdate
from app.repositories.base import BaseRepository


class RescueSessionRepository(BaseRepository[RescueSession]):
    """Repository for RescueSession entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, RescueSession)
    
    async def get_by_child(self, child_id: str) -> list[RescueSession]:
        """Get all rescue sessions for a child"""
        result = await self.session.execute(
            select(RescueSession).where(RescueSession.child_id == child_id)
        )
        return result.scalars().all()
