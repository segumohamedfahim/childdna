"""Analytics Service - Aggregated Operational Insights Engine"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.child import ChildRepository
from app.repositories.guardian import GuardianRepository
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.reunion_record import ReunionRecordRepository
from app.repositories.incident_analysis import IncidentAnalysisRepository
from app.repositories.incident_match import IncidentMatchRepository
from app.repositories.timeline_event import TimelineEventRepository
from app.repositories.alert import AlertRepository
from app.repositories.notification import NotificationRepository
from app.repositories.child_token import ChildTokenRepository
from app.schemas.analytics import (
    AnalyticsMetadata,
    DashboardStatisticsResponse,
    RescueStatisticsResponse,
    IncidentStatisticsResponse,
    MatchStatisticsResponse,
    AlertStatisticsResponse,
    ReunionStatisticsResponse,
    GuardianStatisticsResponse,
    ChildStatisticsResponse,
    SystemHealthResponse,
)
from app.utils.logger import logger


class AnalyticsService:
    """Service for generating aggregated operational analytics.

    All analytics are computed dynamically from existing repositories.
    No database tables, caching, or background jobs are used.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.child_repo = ChildRepository(session)
        self.guardian_repo = GuardianRepository(session)
        self.rescue_repo = RescueSessionRepository(session)
        self.reunion_repo = ReunionRecordRepository(session)
        self.analysis_repo = IncidentAnalysisRepository(session)
        self.match_repo = IncidentMatchRepository(session)
        self.alert_repo = AlertRepository(session)
        self.notification_repo = NotificationRepository(session)
        self.token_repo = ChildTokenRepository(session)

    async def get_dashboard_statistics(self) -> DashboardStatisticsResponse:
        """Return aggregate counts for the main dashboard."""
        now = datetime.now(timezone.utc)
        children = await self.child_repo.get_all()
        guardians = await self.guardian_repo.get_all()
        rescues = await self.rescue_repo.get_all()
        reunions = await self.reunion_repo.get_all()
        analyses = await self.analysis_repo.get_all()
        matches = await self.match_repo.get_all()
        alerts = await self.alert_repo.get_all()
        notifications = await self.notification_repo.get_all()

        return DashboardStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_children=len(children),
            total_guardians=len(guardians),
            total_incidents=len(analyses),
            total_matches=len(matches),
            total_rescue_sessions=len(rescues),
            total_reunions=len(reunions),
            total_alerts=len(alerts),
            total_notifications=len(notifications),
        )

    async def get_rescue_statistics(self) -> RescueStatisticsResponse:
        """Return rescue operation performance statistics."""
        now = datetime.now(timezone.utc)
        rescues = await self.rescue_repo.get_all()

        active = sum(1 for r in rescues if r.status and r.status.value in ("pending", "active"))
        completed = sum(1 for r in rescues if r.status and r.status.value == "complete")
        cancelled = sum(1 for r in rescues if r.status and r.status.value == "cancelled")

        durations = []
        for r in rescues:
            if r.started_at and r.ended_at:
                delta = (r.ended_at - r.started_at).total_seconds() / 60.0
                if delta >= 0:
                    durations.append(delta)

        avg_duration = None
        median_duration = None
        if durations:
            avg_duration = round(sum(durations) / len(durations), 1)
            sorted_durations = sorted(durations)
            mid = len(sorted_durations) // 2
            if len(sorted_durations) % 2 == 0:
                median_duration = round(
                    (sorted_durations[mid - 1] + sorted_durations[mid]) / 2, 1
                )
            else:
                median_duration = round(sorted_durations[mid], 1)

        total_completed_or_failed = completed + cancelled
        success_rate = 0.0
        if total_completed_or_failed > 0:
            success_rate = round(completed / total_completed_or_failed * 100, 1)

        return RescueStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            active_rescues=active,
            completed_rescues=completed,
            failed_rescues=cancelled,
            average_rescue_duration=avg_duration,
            median_rescue_duration=median_duration,
            success_rate=success_rate,
        )

    async def get_incident_statistics(self) -> IncidentStatisticsResponse:
        """Return incident analysis statistics."""
        now = datetime.now(timezone.utc)
        analyses = await self.analysis_repo.get_all()
        rescues = await self.rescue_repo.get_all()

        open_incidents = sum(
            1 for r in rescues
            if r.status and r.status.value in ("pending", "active")
        )
        resolved_incidents = sum(
            1 for r in rescues
            if r.status and r.status.value == "complete"
        )

        confidences = [a.overall_confidence for a in analyses if a.overall_confidence is not None]
        avg_confidence = 0.0
        if confidences:
            avg_confidence = round(sum(confidences) / len(confidences), 2)

        severity_dist: dict[str, int] = {}
        for a in analyses:
            conf = a.overall_confidence or 0.0
            if conf >= 0.7:
                key = "high"
            elif conf >= 0.4:
                key = "medium"
            elif conf > 0.0:
                key = "low"
            else:
                key = "unknown"
            severity_dist[key] = severity_dist.get(key, 0) + 1

        return IncidentStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_incidents=len(analyses),
            open_incidents=open_incidents,
            resolved_incidents=resolved_incidents,
            average_confidence=avg_confidence,
            severity_distribution=severity_dist,
        )

    async def get_match_statistics(self) -> MatchStatisticsResponse:
        """Return incident match statistics."""
        now = datetime.now(timezone.utc)
        matches = await self.match_repo.get_all()

        confirmed = sum(
            1 for m in matches
            if m.match_category in ("identical", "very_high")
        )
        rejected = sum(
            1 for m in matches
            if m.match_category == "low"
        )
        pending = sum(
            1 for m in matches
            if m.match_category == "medium"
        )

        scores = [m.similarity_score for m in matches if m.similarity_score is not None]
        avg_score = 0.0
        if scores:
            avg_score = round(sum(scores) / len(scores), 4)

        return MatchStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_matches=len(matches),
            confirmed_matches=confirmed,
            rejected_matches=rejected,
            pending_matches=pending,
            average_match_score=avg_score,
        )

    async def get_alert_statistics(self) -> AlertStatisticsResponse:
        """Return alert system statistics."""
        now = datetime.now(timezone.utc)
        alerts = await self.alert_repo.get_all()

        active = sum(1 for a in alerts if a.status == "open")
        acknowledged = sum(1 for a in alerts if a.status == "acknowledged")
        resolved = sum(1 for a in alerts if a.status == "resolved")
        dismissed = sum(1 for a in alerts if a.status == "dismissed")

        severity_dist: dict[str, int] = {}
        for a in alerts:
            sev = a.severity or "unknown"
            severity_dist[sev] = severity_dist.get(sev, 0) + 1

        return AlertStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_alerts=len(alerts),
            active_alerts=active,
            acknowledged_alerts=acknowledged,
            resolved_alerts=resolved,
            dismissed_alerts=dismissed,
            severity_distribution=severity_dist,
        )

    async def get_reunion_statistics(self) -> ReunionStatisticsResponse:
        """Return reunion statistics."""
        now = datetime.now(timezone.utc)
        reunions = await self.reunion_repo.get_all()
        rescues = await self.rescue_repo.get_all()

        time_diffs = []
        for reunion in reunions:
            rescue = next(
                (r for r in rescues if str(r.child_id) == str(reunion.child_id)),
                None,
            )
            if rescue and rescue.created_at and reunion.reunion_time:
                delta = (reunion.reunion_time - rescue.created_at).total_seconds() / 3600.0
                if delta >= 0:
                    time_diffs.append(delta)

        avg_time = None
        if time_diffs:
            avg_time = round(sum(time_diffs) / len(time_diffs), 1)

        return ReunionStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            completed_reunions=len(reunions),
            pending_reunions=0,
            average_time_to_reunion=avg_time,
        )

    async def get_guardian_statistics(self) -> GuardianStatisticsResponse:
        """Return guardian statistics."""
        now = datetime.now(timezone.utc)
        guardians = await self.guardian_repo.get_all()
        children = await self.child_repo.get_all()

        guardian_child_counts: dict[str, int] = {}
        for child in children:
            gid = str(child.guardian_id)
            guardian_child_counts[gid] = guardian_child_counts.get(gid, 0) + 1

        guardians_with_children = len(guardian_child_counts)
        avg_children = 0.0
        if guardians:
            total_children_for_guardians = sum(guardian_child_counts.values())
            avg_children = round(total_children_for_guardians / len(guardians), 1)

        return GuardianStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_guardians=len(guardians),
            guardians_with_children=guardians_with_children,
            average_children_per_guardian=avg_children,
        )

    async def get_child_statistics(self) -> ChildStatisticsResponse:
        """Return child population statistics."""
        now = datetime.now(timezone.utc)
        children = await self.child_repo.get_all()
        reunions = await self.reunion_repo.get_all()

        active_cases = sum(
            1 for c in children
            if c.status and c.status.value == "active"
        )

        reunited_ids = set(str(r.child_id) for r in reunions)

        ages = []
        gender_dist: dict[str, int] = {}
        for c in children:
            if c.gender:
                gender_dist[c.gender] = gender_dist.get(c.gender, 0) + 1
            if c.date_of_birth:
                age = self._calculate_age(c.date_of_birth)
                if age is not None:
                    ages.append(age)

        avg_age = None
        if ages:
            avg_age = round(sum(ages) / len(ages), 1)

        return ChildStatisticsResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            total_children=len(children),
            active_cases=active_cases,
            reunited_children=len(reunited_ids),
            average_age=avg_age,
            gender_distribution=gender_dist,
        )

    async def get_system_health(self) -> SystemHealthResponse:
        """Return system health status.

        Checks that repositories respond, AI imports are available,
        and report service modules are importable.
        """
        now = datetime.now(timezone.utc)

        db_status = "operational"
        try:
            await self.child_repo.get_all(limit=1)
        except Exception:
            db_status = "unavailable"

        ai_available = False
        try:
            from app.ai import incident_analyzer, matching_engine
            ai_available = True
        except ImportError:
            ai_available = False

        report_engine = "operational"
        try:
            from app.services.report_service import ReportService
        except ImportError:
            report_engine = "unavailable"

        auth_status = "operational"
        try:
            from app.services.auth_service import AuthService
        except ImportError:
            auth_status = "unavailable"

        return SystemHealthResponse(
            metadata=AnalyticsMetadata(generated_at=now),
            database_status=db_status,
            ai_modules_available=ai_available,
            report_engine_status=report_engine,
            authentication_status=auth_status,
            analytics_status="operational",
        )

    @staticmethod
    def _calculate_age(birth_date) -> Optional[float]:
        """Calculate approximate age in years from a birth date.

        Args:
            birth_date: The date of birth.

        Returns:
            Optional[float]: Age in years, or None if calculation fails.
        """
        from datetime import date
        today = date.today()
        try:
            age = today.year - birth_date.year
            if today.month < birth_date.month or (
                today.month == birth_date.month and today.day < birth_date.day
            ):
                age -= 1
            return float(age)
        except (ValueError, AttributeError):
            return None