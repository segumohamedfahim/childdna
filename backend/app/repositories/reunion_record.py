"""ReunionRecord Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reunion_record import ReunionRecord
from app.schemas.reunion_record import ReunionRecordCreate, ReunionRecordUpdate
from app.repositories.base import BaseRepository


class ReunionRecordRepository(BaseRepository[ReunionRecord]):
    """Repository for ReunionRecord entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ReunionRecord)
    
    async def get_by_child(self, child_id: str) -> list[ReunionRecord]:
        """Get all reunion records for a child"""
        result = await self.session.execute(
            select(ReunionRecord).where(ReunionRecord.child_id == child_id)
        )
        return result.scalars().all()
