"""RescueSession Repository - Data Access Layer"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rescue_session import RescueSession
from app.models.enums import SessionStatus
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
    
    async def activate(self, session_: RescueSession) -> RescueSession:
        """Set session status to active and mark started_at.

        Args:
            session_: The rescue session to activate.

        Returns:
            RescueSession: The updated session.
        """
        session_.status = SessionStatus.ACTIVE
        session_.started_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(session_)
        return session_

    async def complete(self, session_: RescueSession) -> RescueSession:
        """Set session status to complete and mark ended_at.

        Args:
            session_: The rescue session to complete.

        Returns:
            RescueSession: The updated session.
        """
        session_.status = SessionStatus.COMPLETE
        session_.ended_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(session_)
        return session_

    async def cancel(self, session_: RescueSession) -> RescueSession:
        """Set session status to cancelled and mark ended_at.

        Args:
            session_: The rescue session to cancel.

        Returns:
            RescueSession: The updated session.
        """
        session_.status = SessionStatus.CANCELLED
        session_.ended_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(session_)
        return session_

    async def has_active_incident(self, child_id: str) -> bool:
        """Check if a child has any PENDING or ACTIVE rescue session.

        Args:
            child_id: The child UUID to check.

        Returns:
            bool: True if an active incident exists.
        """
        result = await self.session.execute(
            select(RescueSession).where(
                RescueSession.child_id == child_id,
                RescueSession.status.in_([
                    SessionStatus.PENDING,
                    SessionStatus.ACTIVE,
                ]),
            )
        )
        return result.scalar_one_or_none() is not None
