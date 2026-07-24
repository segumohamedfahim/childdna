"""IncidentMatch Repository - Data Access Layer"""
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_match import IncidentMatch
from app.repositories.base import BaseRepository


class IncidentMatchRepository(BaseRepository[IncidentMatch]):
    """Repository for IncidentMatch entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, IncidentMatch)

    async def create(self, data: dict) -> IncidentMatch:
        """Create a single match record from a dict.

        Args:
            data: Dictionary of field values matching the model.

        Returns:
            IncidentMatch: The created match.
        """
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def create_many(
        self, matches: list[dict],
    ) -> list[IncidentMatch]:
        """Batch-insert multiple match records.

        Args:
            matches: List of dictionaries of field values.

        Returns:
            list[IncidentMatch]: The created match records.
        """
        entities = [self.model(**data) for data in matches]
        self.session.add_all(entities)
        await self.session.commit()
        for entity in entities:
            await self.session.refresh(entity)
        return entities

    async def get_by_incident(
        self, incident_id: str,
    ) -> list[IncidentMatch]:
        """Get all matches for a source incident, ordered by score DESC.

        Args:
            incident_id: The source incident UUID.

        Returns:
            list[IncidentMatch]: Match records ordered by similarity_score DESC.
        """
        result = await self.session.execute(
            select(IncidentMatch)
            .where(IncidentMatch.incident_id == incident_id)
            .order_by(IncidentMatch.similarity_score.desc())
        )
        return result.scalars().all()

    async def get_top_matches(
        self, incident_id: str, limit: int = 20,
    ) -> list[IncidentMatch]:
        """Get the top-N matches for a source incident by similarity score.

        Args:
            incident_id: The source incident UUID.
            limit: Maximum number of matches to return.

        Returns:
            list[IncidentMatch]: Top-N match records.
        """
        result = await self.session.execute(
            select(IncidentMatch)
            .where(IncidentMatch.incident_id == incident_id)
            .order_by(IncidentMatch.similarity_score.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_matches(self, incident_id: str) -> None:
        """Delete all match records for a source incident.

        Args:
            incident_id: The source incident UUID.
        """
        await self.session.execute(
            delete(IncidentMatch).where(
                IncidentMatch.incident_id == incident_id
            )
        )
        await self.session.commit()

    async def exists(
        self, incident_id: str, matched_incident_id: str,
    ) -> bool:
        """Check if a match record exists for a given pair.

        Args:
            incident_id: The source incident UUID.
            matched_incident_id: The candidate incident UUID.

        Returns:
            bool: True if a match record exists.
        """
        result = await self.session.execute(
            select(IncidentMatch).where(
                IncidentMatch.incident_id == incident_id,
                IncidentMatch.matched_incident_id == matched_incident_id,
            )
        )
        return result.scalar_one_or_none() is not None
