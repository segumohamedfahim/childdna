"""Timeline Service - Rescue Timeline Event Management"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.timeline_event import TimelineEventRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.schemas.timeline_event import TimelineEventCreate, TimelineEventResponse
from app.models.enums import EventType
from app.core.exceptions import RescueSessionNotFound
from app.utils.logger import logger


class TimelineService:
    """Service for rescue timeline event management.

    Provides helper methods for auto-generating timeline events
    and retrieving ordered event histories.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.event_repo = TimelineEventRepository(session)
        self.rescue_repo = RescueSessionRepository(session)

    async def add_event(
        self,
        incident_id: str,
        event_type: EventType,
        description: str,
        created_by: str = "system",
        latitude: float | None = None,
        longitude: float | None = None,
        location_name: str | None = None,
    ) -> TimelineEventResponse:
        """Add a timeline event to an incident.

        The child_id and rescue_session_id are derived from the
        incident, overriding any caller-supplied values.

        Args:
            incident_id: The rescue session UUID.
            event_type: Type of event from EventType enum.
            description: Human-readable event description.
            created_by: Who created the event (default: "system").
            latitude: Optional event latitude.
            longitude: Optional event longitude.
            location_name: Optional location name.

        Returns:
            TimelineEventResponse: The created event.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Build event data with timestamp (required by model)
        event_data = TimelineEventCreate(
            child_id=incident.child_id,
            rescue_session_id=incident_id,
            event_type=event_type,
            description=description,
            created_by=created_by,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            timestamp=datetime.now(timezone.utc),
        )

        event = await self.event_repo.create(event_data)
        logger.info(
            f"Timeline event added: session_id={incident_id}, "
            f"type={event_type}"
        )

        return TimelineEventResponse.model_validate(event)

    async def get_incident_timeline(
        self, incident_id: str,
    ) -> list[TimelineEventResponse]:
        """Get all timeline events for an incident, ordered by timestamp.

        Args:
            incident_id: The rescue session UUID.

        Returns:
            list[TimelineEventResponse]: Ordered list of events.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        events = await self.event_repo.get_by_session(incident_id)
        return [
            TimelineEventResponse.model_validate(e) for e in events
        ]