"""Reunion Service - Reunion Record Management"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.reunion_record import ReunionRecordRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.child import ChildRepository
from app.repositories.timeline_event import TimelineEventRepository
from app.schemas.reunion_record import (
    ReunionRecordCreate,
    ReunionRecordResponse,
)
from app.schemas.timeline_event import TimelineEventCreate
from app.models.enums import EventType, SessionStatus
from app.core.exceptions import (
    ChildNotFound,
    RescueSessionNotFound,
    InvalidSessionStatusTransition,
)
from app.utils.logger import logger


class ReunionService:
    """Service for reunion record management.

    Records reunions between children and guardians, automatically
    generates REUNION_COMPLETED timeline events, and marks the
    associated rescue session as complete.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.reunion_repo = ReunionRecordRepository(session)
        self.rescue_repo = RescueSessionRepository(session)
        self.child_repo = ChildRepository(session)
        self.event_repo = TimelineEventRepository(session)

    async def record_reunion(
        self, incident_id: str, data: ReunionRecordCreate,
    ) -> ReunionRecordResponse:
        """Record a reunion and close the rescue incident.

        Validates the incident is ACTIVE, overrides the child_id to
        match the incident (security), creates the reunion record,
        generates a REUNION_COMPLETED timeline event, and marks the
        incident as complete.

        Args:
            incident_id: The rescue session UUID.
            data: Reunion record creation data.

        Returns:
            ReunionRecordResponse: The created reunion record.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
            InvalidSessionStatusTransition: If incident is not ACTIVE.
            ChildNotFound: If the child does not exist.
        """
        # Validate incident exists and is ACTIVE
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        if incident.status != SessionStatus.ACTIVE:
            raise InvalidSessionStatusTransition(
                current_status=incident.status.value,
                requested_status="complete",
            )

        # Validate child exists (use incident's child_id, not request body)
        child = await self.child_repo.get_by_id(incident.child_id)
        if not child:
            raise ChildNotFound(child_id=incident.child_id)

        # Create reunion record with child_id from incident (security)
        reunion_payload = data.model_copy(
            update={"child_id": incident.child_id}
        )
        reunion = await self.reunion_repo.create(reunion_payload)

        # Auto-generate REUNION_COMPLETED timeline event
        event = TimelineEventCreate(
            child_id=incident.child_id,
            rescue_session_id=incident_id,
            event_type=EventType.REUNION_COMPLETED,
            description=(
                f"Child reunited with guardian {data.guardian_name}"
            ),
            created_by=data.rescuer_name,
            timestamp=datetime.now(timezone.utc),
        )
        await self.event_repo.create(event)

        # Mark incident as complete
        await self.rescue_repo.complete(incident)

        logger.info(
            f"Reunion recorded: child_id={data.child_id}, "
            f"incident_id={incident_id}"
        )

        return ReunionRecordResponse.model_validate(reunion)

    async def get_child_reunions(
        self, child_id: str,
    ) -> list[ReunionRecordResponse]:
        """Get all reunion records for a child.

        Args:
            child_id: The child UUID.

        Returns:
            list[ReunionRecordResponse]: List of reunion records.
        """
        records = await self.reunion_repo.get_by_child(child_id)
        return [
            ReunionRecordResponse.model_validate(r) for r in records
        ]