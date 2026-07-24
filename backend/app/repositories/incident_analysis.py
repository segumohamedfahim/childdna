"""IncidentAnalysis Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_analysis import IncidentAnalysis
from app.repositories.base import BaseRepository


class IncidentAnalysisRepository(BaseRepository[IncidentAnalysis]):
    """Repository for IncidentAnalysis entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, IncidentAnalysis)

    async def create_from_dict(self, data: dict) -> IncidentAnalysis:
        """Create a new analysis record from a dict.

        Args:
            data: Dictionary of field values matching the model.

        Returns:
            IncidentAnalysis: The created analysis.
        """
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_by_incident(
        self, incident_id: str,
    ) -> Optional[IncidentAnalysis]:
        """Get analysis for a specific incident.

        Args:
            incident_id: The rescue session UUID.

        Returns:
            Optional[IncidentAnalysis]: The analysis or None.
        """
        result = await self.session.execute(
            select(IncidentAnalysis).where(
                IncidentAnalysis.incident_id == incident_id
            )
        )
        return result.scalar_one_or_none()

    async def analysis_exists(self, incident_id: str) -> bool:
        """Check if an incident already has an analysis.

        Args:
            incident_id: The rescue session UUID.

        Returns:
            bool: True if analysis exists.
        """
        result = await self.session.execute(
            select(IncidentAnalysis).where(
                IncidentAnalysis.incident_id == incident_id
            )
        )
        return result.scalar_one_or_none() is not None
