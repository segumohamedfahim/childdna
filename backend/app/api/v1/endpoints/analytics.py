"""Analytics API Endpoints - Aggregated Operational Insights"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
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

router = APIRouter(tags=["analytics"])


@router.get(
    "/analytics/dashboard",
    response_model=DashboardStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get dashboard statistics",
    description="Returns aggregate counts for all major system entities.",
)
async def get_dashboard(
    session: AsyncSession = Depends(get_db),
) -> DashboardStatisticsResponse:
    """Get aggregate dashboard statistics."""
    service = AnalyticsService(session)
    return await service.get_dashboard_statistics()


@router.get(
    "/analytics/rescues",
    response_model=RescueStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get rescue statistics",
    description="Returns rescue operation performance including durations and success rate.",
)
async def get_rescue_stats(
    session: AsyncSession = Depends(get_db),
) -> RescueStatisticsResponse:
    """Get rescue operation statistics."""
    service = AnalyticsService(session)
    return await service.get_rescue_statistics()


@router.get(
    "/analytics/incidents",
    response_model=IncidentStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get incident statistics",
    description="Returns incident analysis statistics including confidence and severity distribution.",
)
async def get_incident_stats(
    session: AsyncSession = Depends(get_db),
) -> IncidentStatisticsResponse:
    """Get incident analysis statistics."""
    service = AnalyticsService(session)
    return await service.get_incident_statistics()


@router.get(
    "/analytics/matches",
    response_model=MatchStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get match statistics",
    description="Returns incident match statistics including confirmation and rejection counts.",
)
async def get_match_stats(
    session: AsyncSession = Depends(get_db),
) -> MatchStatisticsResponse:
    """Get incident match statistics."""
    service = AnalyticsService(session)
    return await service.get_match_statistics()


@router.get(
    "/analytics/alerts",
    response_model=AlertStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get alert statistics",
    description="Returns alert system statistics including severity distribution.",
)
async def get_alert_stats(
    session: AsyncSession = Depends(get_db),
) -> AlertStatisticsResponse:
    """Get alert system statistics."""
    service = AnalyticsService(session)
    return await service.get_alert_statistics()


@router.get(
    "/analytics/reunions",
    response_model=ReunionStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get reunion statistics",
    description="Returns reunion statistics including average time to reunion.",
)
async def get_reunion_stats(
    session: AsyncSession = Depends(get_db),
) -> ReunionStatisticsResponse:
    """Get reunion statistics."""
    service = AnalyticsService(session)
    return await service.get_reunion_statistics()


@router.get(
    "/analytics/guardians",
    response_model=GuardianStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get guardian statistics",
    description="Returns guardian statistics including average children per guardian.",
)
async def get_guardian_stats(
    session: AsyncSession = Depends(get_db),
) -> GuardianStatisticsResponse:
    """Get guardian statistics."""
    service = AnalyticsService(session)
    return await service.get_guardian_statistics()


@router.get(
    "/analytics/children",
    response_model=ChildStatisticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get child statistics",
    description="Returns child population statistics including age and gender distribution.",
)
async def get_child_stats(
    session: AsyncSession = Depends(get_db),
) -> ChildStatisticsResponse:
    """Get child population statistics."""
    service = AnalyticsService(session)
    return await service.get_child_statistics()


@router.get(
    "/analytics/system-health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system health",
    description="Returns system health status including database, AI, and service availability.",
)
async def get_system_health(
    session: AsyncSession = Depends(get_db),
) -> SystemHealthResponse:
    """Get system health status."""
    service = AnalyticsService(session)
    return await service.get_system_health()