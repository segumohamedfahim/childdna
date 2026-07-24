"""Alert Service - Alert Lifecycle Management"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.alert import AlertRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
    AlertSummaryResponse,
)
from app.core.exceptions import RescueSessionNotFound
from app.utils.logger import logger


class AlertService:
    """Service for alert lifecycle management.

    Alerts are generated automatically by the matching engine when
    high-confidence matches are found. Authorities can acknowledge,
    resolve, or dismiss alerts through the API.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.alert_repo = AlertRepository(session)
        self.rescue_repo = RescueSessionRepository(session)

    async def create_alert(
        self, incident_id: str,
        matched_incident_id: str | None,
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        extra_data: dict | None = None,
    ) -> AlertResponse:
        """Create an alert with dedup check.

        If an alert already exists for the same combination of
        (incident_id, matched_incident_id, alert_type), returns
        the existing alert without creating a duplicate.

        Args:
            incident_id: The source incident UUID.
            matched_incident_id: The matched incident UUID (may be None).
            alert_type: Type of alert (e.g., "match_found").
            severity: Alert severity level.
            title: Human-readable alert title.
            description: Detailed alert description.
            extra_data: Optional metadata dict.

        Returns:
            AlertResponse: The created or existing alert.
        """
        # Check for duplicate
        exists = await self.alert_repo.exists(
            incident_id, matched_incident_id, alert_type,
        )
        if exists:
            # Return existing alert
            existing = await self.alert_repo.get_by_incident(incident_id)
            if existing:
                return AlertResponse.model_validate(existing[0])

        # Create alert
        alert_data = AlertCreate(
            incident_id=incident_id,
            matched_incident_id=matched_incident_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            source="matching_engine",
            extra_data=extra_data,
        )
        alert = await self.alert_repo.create(alert_data)

        logger.info(
            f"Alert created: incident_id={incident_id}, "
            f"type={alert_type}, severity={severity}"
        )

        return AlertResponse.model_validate(alert)

    async def get_alert(self, alert_id: str) -> AlertResponse:
        """Get a single alert by ID.

        Args:
            alert_id: The alert UUID.

        Returns:
            AlertResponse: The alert.

        Raises:
            AlertNotFound: If the alert does not exist.
        """
        from app.core.exceptions import AlertNotFound
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFound(alert_id=alert_id)
        return AlertResponse.model_validate(alert)

    async def list_alerts(
        self,
        status: str | None = None,
        severity: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> AlertListResponse:
        """List alerts with optional filters and pagination.

        Args:
            status: Optional status filter.
            severity: Optional severity filter.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            AlertListResponse: Paginated alert list.
        """
        if status:
            alerts = await self.alert_repo.get_by_status(
                status, skip, limit
            )
        elif severity:
            alerts = await self.alert_repo.get_by_severity(
                severity, skip, limit
            )
        else:
            alerts = await self.alert_repo.get_all(skip, limit)

        return AlertListResponse(
            alerts=[AlertResponse.model_validate(a) for a in alerts],
            total=len(alerts),
            skip=skip,
            limit=limit,
        )

    async def acknowledge_alert(
        self, alert_id: str, acknowledged_by: str,
    ) -> AlertResponse:
        """Mark an alert as ACKNOWLEDGED.

        Validates the alert exists and is currently OPEN.

        Args:
            alert_id: The alert UUID.
            acknowledged_by: Name of the person acknowledging.

        Returns:
            AlertResponse: The updated alert.

        Raises:
            AlertNotFound: If the alert does not exist.
        """
        from app.core.exceptions import AlertNotFound
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFound(alert_id=alert_id)

        if alert.status != "open":
            from app.core.exceptions import InvalidAlertStatusTransition
            raise InvalidAlertStatusTransition(
                current_status=alert.status,
                requested_status="acknowledged",
            )

        alert = await self.alert_repo.update_status(
            alert_id, "acknowledged",
            actor=acknowledged_by,
            timestamp=datetime.now(timezone.utc),
        )

        logger.info(
            f"Alert acknowledged: id={alert_id}, "
            f"by={acknowledged_by}"
        )

        return AlertResponse.model_validate(alert)

    async def resolve_alert(
        self, alert_id: str, resolved_by: str,
    ) -> AlertResponse:
        """Mark an alert as RESOLVED.

        Validates the alert exists and is currently ACKNOWLEDGED.

        Args:
            alert_id: The alert UUID.
            resolved_by: Name of the person resolving.

        Returns:
            AlertResponse: The updated alert.

        Raises:
            AlertNotFound: If the alert does not exist.
        """
        from app.core.exceptions import AlertNotFound
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFound(alert_id=alert_id)

        if alert.status not in ("open", "acknowledged"):
            from app.core.exceptions import InvalidAlertStatusTransition
            raise InvalidAlertStatusTransition(
                current_status=alert.status,
                requested_status="resolved",
            )

        alert = await self.alert_repo.update_status(
            alert_id, "resolved",
            actor=resolved_by,
            timestamp=datetime.now(timezone.utc),
        )

        logger.info(
            f"Alert resolved: id={alert_id}, "
            f"by={resolved_by}"
        )

        return AlertResponse.model_validate(alert)

    async def dismiss_alert(
        self, alert_id: str, dismissed_by: str,
    ) -> AlertResponse:
        """Dismiss an alert.

        Dismissal can be performed from any non-terminal state.

        Args:
            alert_id: The alert UUID.
            dismissed_by: Name of the person dismissing.

        Returns:
            AlertResponse: The updated alert.

        Raises:
            AlertNotFound: If the alert does not exist.
        """
        from app.core.exceptions import AlertNotFound
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise AlertNotFound(alert_id=alert_id)

        if alert.status in ("resolved", "dismissed"):
            from app.core.exceptions import InvalidAlertStatusTransition
            raise InvalidAlertStatusTransition(
                current_status=alert.status,
                requested_status="dismissed",
            )

        alert = await self.alert_repo.update_status(
            alert_id, "dismissed",
            actor=dismissed_by,
            timestamp=datetime.now(timezone.utc),
        )

        logger.info(
            f"Alert dismissed: id={alert_id}, "
            f"by={dismissed_by}"
        )

        return AlertResponse.model_validate(alert)

    async def get_alert_summary(self) -> AlertSummaryResponse:
        """Return aggregate alert counts by severity and status.

        Returns:
            AlertSummaryResponse: Summary counts.
        """
        summary = await self.alert_repo.get_summary()

        by_status = summary.get("by_status", {})
        return AlertSummaryResponse(
            total_open=by_status.get("open", 0),
            total_acknowledged=by_status.get("acknowledged", 0),
            total_resolved=by_status.get("resolved", 0),
            total_dismissed=by_status.get("dismissed", 0),
            by_severity=summary.get("by_severity", {}),
            by_status=by_status,
        )

    @staticmethod
    def determine_severity(match_category: str) -> str:
        """Map a MatchCategory to an AlertSeverity.

        Args:
            match_category: The match category string.

        Returns:
            str: The corresponding alert severity.
        """
        mapping = {
            "identical": "critical",
            "very_high": "high",
            "high": "medium",
            "medium": "low",
            "low": "low",
            "no_match": "low",
        }
        return mapping.get(match_category, "low")

    @staticmethod
    def build_alert_title(
        match_category: str, similarity_score: float,
    ) -> str:
        """Build a human-readable alert title from match data.

        Args:
            match_category: The match category string.
            similarity_score: The similarity score.

        Returns:
            str: Alert title.
        """
        category_labels = {
            "identical": "Identical Match Found",
            "very_high": "Very High Confidence Match",
            "high": "High Confidence Match",
            "medium": "Medium Confidence Match",
            "low": "Low Confidence Match",
        }
        label = category_labels.get(
            match_category, "Potential Match Found"
        )
        return f"{label} ({similarity_score:.1%})"