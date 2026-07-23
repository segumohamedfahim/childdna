"""TimelineEvent Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.timeline_event import TimelineEvent
from app.schemas.timeline_event import TimelineEventCreate, TimelineEventUpdate
from app.repositories.base import BaseRepository


class TimelineEventRepository(BaseRepository[TimelineEvent]):
    """Repository for TimelineEvent entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, TimelineEvent)
    
    async def get_by_child(self, child_id: str) -> list[TimelineEvent]:
        """Get all timeline events for a child"""
        result = await self.session.execute(
            select(TimelineEvent).where(TimelineEvent.child_id == child_id)
        )
        return result.scalars().all()
    
    async def get_by_session(self, session_id: str) -> list[TimelineEvent]:
        """Get all timeline events for a rescue session"""
        result = await self.session.execute(
            select(TimelineEvent).where(TimelineEvent.rescue_session_id == session_id)
        )
        return result.scalars().all()
