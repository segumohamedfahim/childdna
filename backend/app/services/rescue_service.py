"""Rescue Service - Incident Lifecycle Management"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.child import ChildRepository
from app.schemas.rescue_session import (
    RescueSessionCreate,
    RescueSessionUpdate,
    RescueSessionResponse,
)
from app.models.enums import EventType, SessionStatus
from app.core.exceptions import (
    ChildNotFound,
    RescueSessionNotFound,
    InvalidSessionStatusTransition,
    ActiveRescueSessionExists,
)
from app.utils.rescue_rules import is_transition_allowed
from app.services.timeline_service import TimelineService
from app.utils.logger import logger


class RescueService:
    """Service for rescue incident lifecycle management.

    Handles incident creation, retrieval, update with automatic
    timeline event generation for status changes and location updates.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rescue_repo = RescueSessionRepository(session)
        self.child_repo = ChildRepository(session)
        self.timeline_service = TimelineService(session)

    async def create_incident(
        self, data: RescueSessionCreate,
    ) -> RescueSessionResponse:
        """Create a new rescue incident.

        Validates the child exists and does not already have an
        active incident. Automatically generates a INCIDENT_CREATED
        timeline event.

        Args:
            data: Rescue session creation data.

        Returns:
            RescueSessionResponse: The created incident.

        Raises:
            ChildNotFound: If the child does not exist.
            ActiveRescueSessionExists: If child has PENDING or ACTIVE incident.
        """
        # Validate child exists
        child = await self.child_repo.get_by_id(data.child_id)
        if not child:
            raise ChildNotFound(child_id=data.child_id)

        # Check for duplicate active incident
        if await self.rescue_repo.has_active_incident(data.child_id):
            raise ActiveRescueSessionExists(child_id=data.child_id)

        # Create incident (status defaults to PENDING via model)
        incident = await self.rescue_repo.create(data)

        # Auto-generate timeline event
        await self.timeline_service.add_event(
            incident_id=incident.id,
            event_type=EventType.INCIDENT_CREATED,
            description="Rescue incident created",
            latitude=data.latitude,
            longitude=data.longitude,
            location_name=data.location_name,
        )

        logger.info(
            f"Rescue incident created: id={incident.id}, "
            f"child_id={data.child_id}"
        )

        return RescueSessionResponse.model_validate(incident)

    async def get_incident(
        self, incident_id: str,
    ) -> RescueSessionResponse:
        """Get a rescue incident by ID.

        Args:
            incident_id: The incident UUID.

        Returns:
            RescueSessionResponse: The incident.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        return RescueSessionResponse.model_validate(incident)

    async def list_incidents(
        self, skip: int = 0, limit: int = 10,
    ) -> list[RescueSessionResponse]:
        """List all rescue incidents with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[RescueSessionResponse]: List of incidents.
        """
        incidents = await self.rescue_repo.get_all(skip=skip, limit=limit)
        return [
            RescueSessionResponse.model_validate(i) for i in incidents
        ]

    async def update_incident(
        self, incident_id: str, data: RescueSessionUpdate,
    ) -> RescueSessionResponse:
        """Update a rescue incident.

        Validates status transitions and delegates persistence to
        repository methods. Automatically generates STATUS_CHANGED
        timeline events when status changes.

        Args:
            incident_id: The incident UUID.
            data: Rescue session update data.

        Returns:
            RescueSessionResponse: The updated incident.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
            InvalidSessionStatusTransition: If the status transition is invalid.
        """
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Handle status transitions through repository methods
        if data.status is not None and data.status != incident.status:
            if not is_transition_allowed(incident.status, data.status):
                raise InvalidSessionStatusTransition(
                    current_status=incident.status.value,
                    requested_status=data.status.value,
                )

            old_status = incident.status.value

            # Delegate to repository for persistence
            if data.status == SessionStatus.ACTIVE:
                incident = await self.rescue_repo.activate(incident)
            elif data.status == SessionStatus.COMPLETE:
                incident = await self.rescue_repo.complete(incident)
            elif data.status == SessionStatus.CANCELLED:
                incident = await self.rescue_repo.cancel(incident)

            # Auto-generate status change timeline event
            await self.timeline_service.add_event(
                incident_id=incident_id,
                event_type=EventType.STATUS_CHANGED,
                description=(
                    f"Status changed from {old_status} "
                    f"to {incident.status.value}"
                ),
            )

            logger.info(
                f"Rescue incident status updated: id={incident_id}, "
                f"status={incident.status.value}"
            )

        # Handle non-status field updates
        status_sent = data.status is not None
        non_status_fields = data.model_dump(exclude_unset=True)
        if status_sent:
            non_status_fields.pop("status", None)

        if non_status_fields:
            # Create filtered update without status to avoid double-write
            filtered_data = data.model_copy(update=non_status_fields)
            incident = await self.rescue_repo.update(incident, filtered_data)

            # Auto-generate location update if lat/lng changed
            lat_lng_changed = (
                "latitude" in non_status_fields
                or "longitude" in non_status_fields
            )
            if lat_lng_changed:
                loc_name = data.location_name or "Unknown location"
                await self.timeline_service.add_event(
                    incident_id=incident_id,
                    event_type=EventType.LOCATION_UPDATED,
                    description=f"Location updated to {loc_name}",
                    latitude=data.latitude,
                    longitude=data.longitude,
                    location_name=data.location_name,
                )

            logger.info(
                f"Rescue incident updated: id={incident_id}"
            )

        return RescueSessionResponse.model_validate(incident)

    async def get_child_incidents(
        self, child_id: str,
    ) -> list[RescueSessionResponse]:
        """Get all incidents for a child.

        Args:
            child_id: The child UUID.

        Returns:
            list[RescueSessionResponse]: List of incidents.
        """
        incidents = await self.rescue_repo.get_by_child(child_id)
        return [
            RescueSessionResponse.model_validate(i) for i in incidents
        ]