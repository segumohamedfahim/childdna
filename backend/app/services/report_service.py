"""Report Service - Mission Report Generation Engine"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.child import ChildRepository
from app.repositories.guardian import GuardianRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.reunion_record import ReunionRecordRepository
from app.repositories.incident_analysis import IncidentAnalysisRepository
from app.repositories.incident_match import IncidentMatchRepository
from app.repositories.timeline_event import TimelineEventRepository
from app.repositories.alert import AlertRepository
from app.repositories.child_token import ChildTokenRepository
from app.schemas.report import (
    ReportMetadata,
    IncidentReportResponse,
    RescueReportResponse,
    ReunionReportResponse,
    ChildReportResponse,
    SystemReportResponse,
    TimelineEventItem,
    RescueHistoryItem,
)
from app.core.exceptions import (
    RescueSessionNotFound,
    AnalysisNotFound,
)
from app.utils.logger import logger


class ReportService:
    """Service for generating mission reports from existing system data.

    All reports are generated on-demand from existing services and repositories.
    No new database tables are required.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.child_repo = ChildRepository(session)
        self.guardian_repo = GuardianRepository(session)
        self.rescue_repo = RescueSessionRepository(session)
        self.reunion_repo = ReunionRecordRepository(session)
        self.analysis_repo = IncidentAnalysisRepository(session)
        self.match_repo = IncidentMatchRepository(session)
        self.event_repo = TimelineEventRepository(session)
        self.alert_repo = AlertRepository(session)
        self.token_repo = ChildTokenRepository(session)

    async def generate_incident_report(
        self, incident_analysis_id: str,
    ) -> IncidentReportResponse:
        """Generate a report for an incident analysis.

        Args:
            incident_analysis_id: The incident analysis UUID.

        Returns:
            IncidentReportResponse: Structured incident report.

        Raises:
            AnalysisNotFound: If the analysis does not exist.
        """
        now = datetime.now(timezone.utc)
        analysis = await self.analysis_repo.get_by_id(incident_analysis_id)
        if not analysis:
            raise AnalysisNotFound(incident_id=incident_analysis_id)

        incident = await self.rescue_repo.get_by_id(analysis.incident_id)

        child_name = None
        if incident:
            child = await self.child_repo.get_by_id(incident.child_id)
            child_name = child.full_name if child else None

        # Determine severity from confidence
        severity = "unknown"
        if analysis.overall_confidence >= 0.7:
            severity = "high"
        elif analysis.overall_confidence >= 0.4:
            severity = "medium"
        elif analysis.overall_confidence > 0.0:
            severity = "low"

        recommendations = self._build_recommendations(analysis)

        return IncidentReportResponse(
            metadata=ReportMetadata(
                generated_at=now,
                report_type="incident_analysis",
            ),
            incident_id=str(analysis.incident_id),
            incident_status=incident.status.value if incident else None,
            incident_priority=incident.priority if incident else None,
            child_id=str(incident.child_id) if incident else None,
            child_name=child_name,
            analysis_summary=analysis.raw_text[:500] if analysis.raw_text else None,
            analysis_engine=analysis.analysis_engine,
            overall_confidence=analysis.overall_confidence,
            severity=severity,
            recommendations=recommendations,
            analysis_timestamp=analysis.created_at,
            generated_at=now,
        )

    async def generate_rescue_report(
        self, rescue_session_id: str,
    ) -> RescueReportResponse:
        """Generate a report for a rescue session.

        Args:
            rescue_session_id: The rescue session UUID.

        Returns:
            RescueReportResponse: Structured rescue report.

        Raises:
            RescueSessionNotFound: If the rescue session does not exist.
        """
        now = datetime.now(timezone.utc)
        incident = await self.rescue_repo.get_by_id(rescue_session_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=rescue_session_id)

        child_name = None
        child = await self.child_repo.get_by_id(incident.child_id)
        child_name = child.full_name if child else None

        events = await self.event_repo.get_by_session(rescue_session_id)
        timeline = [
            TimelineEventItem(
                event_type=e.event_type,
                description=e.description,
                timestamp=e.timestamp,
                created_by=e.created_by,
            )
            for e in events
        ]

        duration_minutes = None
        if incident.started_at and incident.ended_at:
            delta = incident.ended_at - incident.started_at
            duration_minutes = delta.total_seconds() / 60.0

        outcome = None
        if incident.status:
            outcome_map = {
                "complete": "successfully completed",
                "cancelled": "cancelled",
                "active": "in progress",
                "pending": "pending",
            }
            outcome = outcome_map.get(incident.status.value, incident.status.value)

        return RescueReportResponse(
            metadata=ReportMetadata(
                generated_at=now,
                report_type="rescue_session",
            ),
            rescue_id=str(incident.id),
            child_id=str(incident.child_id),
            child_name=child_name,
            status=incident.status.value if incident.status else None,
            priority=incident.priority,
            rescuer_name=incident.rescuer_name,
            rescuer_phone=incident.rescuer_phone,
            location_name=incident.location_name,
            notes=incident.notes,
            started_at=incident.started_at,
            ended_at=incident.ended_at,
            duration_minutes=round(duration_minutes, 1) if duration_minutes else None,
            timeline=timeline,
            outcome=outcome,
            generated_at=now,
        )

    async def generate_reunion_report(
        self, reunion_record_id: str,
    ) -> ReunionReportResponse:
        """Generate a report for a reunion record.

        Args:
            reunion_record_id: The reunion record UUID.

        Returns:
            ReunionReportResponse: Structured reunion report.

        Raises:
            ChildNotFound: If the reunion record does not exist.
        """
        now = datetime.now(timezone.utc)
        from app.core.exceptions import ChildNotFound

        record = await self.reunion_repo.get_by_id(reunion_record_id)
        if not record:
            raise ChildNotFound(child_id=reunion_record_id)

        child_name = None
        child = await self.child_repo.get_by_id(record.child_id)
        child_name = child.full_name if child else None

        return ReunionReportResponse(
            metadata=ReportMetadata(
                generated_at=now,
                report_type="reunion_record",
            ),
            reunion_id=str(record.id),
            child_id=str(record.child_id),
            child_name=child_name,
            guardian_name=record.guardian_name,
            rescuer_name=record.rescuer_name,
            reunion_time=record.reunion_time,
            verification_method=record.verification_method,
            remarks=record.remarks,
            verification_status="verified",
            generated_at=now,
        )

    async def generate_child_report(
        self, child_id: str,
    ) -> ChildReportResponse:
        """Generate a comprehensive report for a child.

        Args:
            child_id: The child UUID.

        Returns:
            ChildReportResponse: Structured child report.

        Raises:
            ChildNotFound: If the child does not exist.
        """
        from app.core.exceptions import ChildNotFound
        now = datetime.now(timezone.utc)

        child = await self.child_repo.get_by_id(child_id)
        if not child:
            raise ChildNotFound(child_id=child_id)

        guardian = await self.guardian_repo.get_by_id(child.guardian_id)

        rescues = await self.rescue_repo.get_by_child(child_id)
        reunions = await self.reunion_repo.get_by_child(child_id)
        events = await self.event_repo.get_by_child(child_id)

        rescue_history = [
            RescueHistoryItem(
                rescue_id=str(r.id),
                status=r.status.value if r.status else None,
                created_at=r.created_at,
                outcome=(
                    "completed" if r.status and r.status.value == "complete"
                    else "cancelled" if r.status and r.status.value == "cancelled"
                    else "active" if r.status and r.status.value == "active"
                    else "pending"
                ),
            )
            for r in rescues
        ]

        timeline_summary = (
            f"{len(events)} timeline events recorded "
            f"across {len(rescues)} rescue incident(s)"
        )

        reunion_status = "none"
        if reunions:
            reunion_status = "reunited"

        return ChildReportResponse(
            metadata=ReportMetadata(
                generated_at=now,
                report_type="child_profile",
            ),
            child_id=str(child.id),
            full_name=child.full_name,
            date_of_birth=str(child.date_of_birth) if child.date_of_birth else None,
            gender=child.gender,
            blood_group=child.blood_group,
            status=child.status.value if child.status else None,
            guardian_id=str(guardian.id) if guardian else None,
            guardian_name=guardian.full_name if guardian else None,
            guardian_email=guardian.email if guardian else None,
            guardian_phone=guardian.phone if guardian else None,
            rescue_history=rescue_history,
            incident_count=len(rescues),
            reunion_count=len(reunions),
            timeline_summary=timeline_summary,
            reunion_status=reunion_status,
            generated_at=now,
        )

    async def generate_system_report(self) -> SystemReportResponse:
        """Generate a system-wide aggregated statistics report.

        Returns:
            SystemReportResponse: Aggregated system statistics.
        """
        now = datetime.now(timezone.utc)

        children = await self.child_repo.get_all()
        guardians = await self.guardian_repo.get_all()
        rescues = await self.rescue_repo.get_all()
        reunions = await self.reunion_repo.get_all()
        tokens = await self.token_repo.get_all()
        alert_summary = await self.alert_repo.get_summary()

        active_rescues = sum(
            1 for r in rescues
            if r.status and r.status.value in ("pending", "active")
        )
        completed_reunions = len(reunions)

        by_severity = alert_summary.get("by_severity", {})
        by_status = alert_summary.get("by_status", {})

        return SystemReportResponse(
            metadata=ReportMetadata(
                generated_at=now,
                report_type="system_overview",
            ),
            total_children=len(children),
            total_guardians=len(guardians),
            total_tokens=len(tokens),
            active_rescues=active_rescues,
            completed_reunions=completed_reunions,
            active_alerts=by_status.get("open", 0),
            total_incidents=len(rescues),
            total_alert_open=by_status.get("open", 0),
            total_alert_acknowledged=by_status.get("acknowledged", 0),
            total_alert_resolved=by_status.get("resolved", 0),
            total_alert_dismissed=by_status.get("dismissed", 0),
            by_severity=dict(by_severity),
            by_status=dict(by_status),
            generated_at=now,
        )

    def _build_recommendations(self, analysis) -> list[str]:
        """Build recommendation list from analysis data.

        Args:
            analysis: The IncidentAnalysis model instance.

        Returns:
            list[str]: Human-readable recommendations.
        """
        recommendations = []

        if analysis.overall_confidence >= 0.7:
            recommendations.append(
                "High confidence analysis — review for immediate action"
            )
        elif analysis.overall_confidence >= 0.4:
            recommendations.append(
                "Medium confidence analysis — verify details before action"
            )
        elif analysis.overall_confidence > 0.0:
            recommendations.append(
                "Low confidence analysis — additional information recommended"
            )

        if analysis.gender and analysis.gender_confidence < 0.5:
            recommendations.append(
                "Gender identification confidence is low — verify visually"
            )

        if analysis.estimated_age_min and analysis.estimated_age_max:
            recommendations.append(
                f"Estimated age range: {analysis.estimated_age_min}-"
                f"{analysis.estimated_age_max} years"
            )

        if not recommendations:
            recommendations.append("No actionable recommendations available")

        return recommendations