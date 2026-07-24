"""Notification Repository - Data Access Layer for Notifications"""
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def get_by_guardian(
        self, guardian_id: str, skip: int = 0, limit: int = 20,
    ) -> list[Notification]:
        """Get notifications for a guardian, newest first.

        Args:
            guardian_id: The guardian UUID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[Notification]: Notifications ordered by created_at DESC.
        """
        result = await self.session.execute(
            select(Notification)
            .where(Notification.guardian_id == guardian_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 20,
    ) -> list[Notification]:
        """Filter notifications by delivery status.

        Args:
            status: Notification status to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[Notification]: Notifications matching the status.
        """
        result = await self.session.execute(
            select(Notification)
            .where(Notification.status == status)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unread_count(self, guardian_id: str) -> int:
        """Count unread notifications for a guardian.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            int: Count of notifications with read_at IS NULL.
        """
        result = await self.session.execute(
            select(func.count(Notification.id))
            .where(
                Notification.guardian_id == guardian_id,
                Notification.read_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: str) -> Notification:
        """Mark a single notification as read.

        Args:
            notification_id: The notification UUID.

        Returns:
            Notification: The updated notification.
        """
        from datetime import datetime, timezone
        notification = await self.get_by_id(notification_id)
        if notification:
            notification.read_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(notification)
        return notification

    async def mark_all_as_read(self, guardian_id: str) -> int:
        """Mark all unread notifications for a guardian as read.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            int: Number of notifications updated.
        """
        from datetime import datetime, timezone
        result = await self.session.execute(
            update(Notification)
            .where(
                Notification.guardian_id == guardian_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=datetime.now(timezone.utc))
        )
        await self.session.commit()
        return result.rowcount

    async def get_summary(self, guardian_id: str) -> dict:
        """Return notification counts by type and status for a guardian.

        Args:
            guardian_id: The guardian UUID.

        Returns:
            dict: Summary with by_type and by_status counts.
        """
        # Count by type
        type_result = await self.session.execute(
            select(Notification.notification_type, func.count(Notification.id))
            .where(Notification.guardian_id == guardian_id)
            .group_by(Notification.notification_type)
        )
        by_type = dict(type_result.all())

        # Count by status
        status_result = await self.session.execute(
            select(Notification.status, func.count(Notification.id))
            .where(Notification.guardian_id == guardian_id)
            .group_by(Notification.status)
        )
        by_status = dict(status_result.all())

        return {
            "by_type": by_type,
            "by_status": by_status,
        }