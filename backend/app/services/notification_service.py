"""Notification Service - Guardian Notification Dispatch"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.notification import NotificationRepository
from app.repositories.guardian import GuardianRepository
from app.repositories.child import ChildRepository
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationSummaryResponse,
)
from app.core.exceptions import GuardianNotFound, ChildNotFound
from app.utils.logger import logger


class NotificationService:
    """Service for guardian notification dispatch.

    Notifications are created by rescue and reunion services when
    incidents change status or reunions are completed. Delivery
    is in-app only for this sprint; future sprints can add
    email/SMS channels.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.notification_repo = NotificationRepository(session)
        self.guardian_repo = GuardianRepository(session)
        self.child_repo = ChildRepository(session)

    async def dispatch(
        self,
        guardian_id: str,
        child_id: str | None = None,
        incident_id: str | None = None,
        notification_type: str = "status_changed",
        title: str = "",
        message: str = "",
        extra_data: dict | None = None,
    ) -> NotificationResponse:
        """Create a notification with PENDING status.

        Args:
            guardian_id: The guardian UUID.
            child_id: Optional child UUID.
            incident_id: Optional incident UUID.
            notification_type: Type of notification.
            title: Notification title.
            message: Notification message body.
            extra_data: Optional metadata dict.

        Returns:
            NotificationResponse: The created notification.

        Raises:
            GuardianNotFound: If the guardian does not exist.
        """
        # Validate guardian exists
        guardian = await self.guardian_repo.get_by_id(guardian_id)
        if not guardian:
            raise GuardianNotFound(guardian_id=guardian_id)

        # Create notification via base repository
        from app.schemas.notification import NotificationResponse
        from app.models.notification import Notification

        notification = Notification(
            guardian_id=guardian_id,
            child_id=child_id,
            incident_id=incident_id,
            notification_type=notification_type,
            channel="in_app",
            status="pending",
            title=title,
            message=message,
            extra_data=extra_data,
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)

        logger.info(
            f"Notification dispatched: guardian_id={guardian_id}, "
            f"type={notification_type}"
        )

        return NotificationResponse.model_validate(notification)

    async def get_notifications(
        self, guardian_id: str, skip: int = 0, limit: int = 20,
    ) -> NotificationListResponse:
        """List notifications for a guardian, newest first.

        Args:
            guardian_id: The guardian UUID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            NotificationListResponse: Paginated notification list.
        """
        notifications = await self.notification_repo.get_by_guardian(
            guardian_id, skip, limit
        )

        return NotificationListResponse(
            notifications=[
                NotificationResponse.model_validate(n)
                for n in notifications
            ],
            total=len(notifications),
            skip=skip,
            limit=limit,
        )

    async def get_unread_count(self, guardian_id: str) -> int:
        """Return count of unread notifications for a guardian.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            int: Unread notification count.
        """
        return await self.notification_repo.get_unread_count(guardian_id)

    async def mark_as_read(
        self, notification_id: str,
    ) -> NotificationResponse:
        """Mark a single notification as read.

        Args:
            notification_id: The notification UUID.

        Returns:
            NotificationResponse: The updated notification.
        """
        notification = await self.notification_repo.mark_as_read(
            notification_id
        )
        return NotificationResponse.model_validate(notification)

    async def mark_all_as_read(self, guardian_id: str) -> int:
        """Mark all notifications for a guardian as read.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            int: Number of notifications marked as read.
        """
        return await self.notification_repo.mark_all_as_read(guardian_id)

    async def get_summary(
        self, guardian_id: str,
    ) -> NotificationSummaryResponse:
        """Return notification summary counts for a guardian.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            NotificationSummaryResponse: Summary counts.
        """
        unread_count = await self.notification_repo.get_unread_count(
            guardian_id
        )
        summary = await self.notification_repo.get_summary(guardian_id)

        by_status = summary.get("by_status", {})
        total_sent = sum(by_status.values())

        return NotificationSummaryResponse(
            total_unread=unread_count,
            total_sent=total_sent,
            by_type=summary.get("by_type", {}),
            by_status=by_status,
        )

    async def resolve_guardian(self, child_id: str) -> str:
        """Resolve guardian_id from child_id.

        Args:
            child_id: The child UUID.

        Returns:
            str: The guardian UUID.

        Raises:
            ChildNotFound: If the child does not exist.
        """
        child = await self.child_repo.get_by_id(child_id)
        if not child:
            raise ChildNotFound(child_id=child_id)
        return str(child.guardian_id)

    @staticmethod
    def build_message(
        notification_type: str, context: dict,
    ) -> tuple[str, str]:
        """Build (title, message) from notification type and context.

        Args:
            notification_type: The notification type string.
            context: Dict with relevant context (child_name, status, etc.).

        Returns:
            tuple: (title, message) strings.
        """
        child_name = context.get("child_name", "Your child")

        templates = {
            "incident_created": (
                f"Rescue Started for {child_name}",
                f"A rescue incident has been created for {child_name}. "
                "Authorities have been notified and are responding.",
            ),
            "status_changed": (
                f"Rescue Status Updated for {child_name}",
                f"The status of the rescue incident for {child_name} "
                f"has changed to {context.get('status', 'updated')}.",
            ),
            "reunion_completed": (
                f"Reunited with {child_name}",
                f"Great news! {child_name} has been safely reunited "
                f"with {context.get('guardian_name', 'the guardian')}.",
            ),
            "match_found": (
                f"Potential Match Found for {child_name}",
                f"A potential match has been identified for {child_name}. "
                "Authorities are reviewing the details.",
            ),
        }

        return templates.get(
            notification_type,
            ("Notification", f"Update regarding {child_name}"),
        )