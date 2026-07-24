"""Alert Repository - Data Access Layer for Alerts"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """Repository for Alert entity"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Alert)

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 20,
    ) -> list[Alert]:
        """Filter alerts by status, ordered by created_at DESC.

        Args:
            status: Alert status to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[Alert]: Alerts matching the status.
        """
        result = await self.session.execute(
            select(Alert)
            .where(Alert.status == status)
            .order_by(Alert.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_severity(
        self, severity: str, skip: int = 0, limit: int = 20,
    ) -> list[Alert]:
        """Filter alerts by severity, ordered by created_at DESC.

        Args:
            severity: Alert severity to filter by.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[Alert]: Alerts matching the severity.
        """
        result = await self.session.execute(
            select(Alert)
            .where(Alert.severity == severity)
            .order_by(Alert.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_incident(
        self, incident_id: str,
    ) -> list[Alert]:
        """Get all alerts for an incident.

        Args:
            incident_id: The incident UUID.

        Returns:
            list[Alert]: Alerts for the incident.
        """
        result = await self.session.execute(
            select(Alert)
            .where(Alert.incident_id == incident_id)
            .order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def get_open_alerts(
        self, skip: int = 0, limit: int = 20,
    ) -> list[Alert]:
        """Get alerts with status=OPEN.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            list[Alert]: Open alerts.
        """
        return await self.get_by_status("open", skip, limit)

    async def get_summary(self) -> dict:
        """Return counts grouped by severity and status.

        Returns:
            dict: Summary with by_severity and by_status counts.
        """
        # Count by severity
        severity_result = await self.session.execute(
            select(Alert.severity, func.count(Alert.id))
            .group_by(Alert.severity)
        )
        by_severity = dict(severity_result.all())

        # Count by status
        status_result = await self.session.execute(
            select(Alert.status, func.count(Alert.id))
            .group_by(Alert.status)
        )
        by_status = dict(status_result.all())

        return {
            "by_severity": by_severity,
            "by_status": by_status,
        }

    async def exists(
        self, incident_id: str, matched_incident_id: Optional[str],
        alert_type: str,
    ) -> bool:
        """Check if an alert exists for this combination.

        Args:
            incident_id: The source incident UUID.
            matched_incident_id: The matched incident UUID (may be None).
            alert_type: The alert type string.

        Returns:
            bool: True if a matching alert exists.
        """
        query = select(Alert).where(
            Alert.incident_id == incident_id,
            Alert.alert_type == alert_type,
        )
        if matched_incident_id is None:
            query = query.where(Alert.matched_incident_id.is_(None))
        else:
            query = query.where(
                Alert.matched_incident_id == matched_incident_id
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def update_status(
        self, alert_id: str, status: str,
        actor: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Alert:
        """Update alert status with optional actor and timestamp.

        Args:
            alert_id: The alert UUID.
            status: New status value.
            actor: Name of the person performing the action.
            timestamp: When the action occurred.

        Returns:
            Alert: The updated alert.
        """
        alert = await self.get_by_id(alert_id)
        if not alert:
            raise ValueError(f"Alert not found: {alert_id}")

        alert.status = status
        if actor:
            if status == "acknowledged":
                alert.acknowledged_by = actor
                alert.acknowledged_at = timestamp or datetime.now()
            elif status == "resolved":
                alert.resolved_by = actor
                alert.resolved_at = timestamp or datetime.now()

        await self.session.commit()
        await self.session.refresh(alert)
        return alert