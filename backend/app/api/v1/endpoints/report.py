"""Report API Endpoints - Mission Report Generation"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.report_service import ReportService
from app.schemas.report import (
    IncidentReportResponse,
    RescueReportResponse,
    ReunionReportResponse,
    ChildReportResponse,
    SystemReportResponse,
)

router = APIRouter(tags=["reports"])


@router.get(
    "/reports/system",
    response_model=SystemReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get system-wide report",
    description=(
        "Returns aggregated system-wide statistics including total "
        "children, guardians, active rescues, completed reunions, "
        "and alert breakdowns."
    ),
)
async def get_system_report(
    session: AsyncSession = Depends(get_db),
) -> SystemReportResponse:
    """Generate a system-wide aggregated statistics report."""
    service = ReportService(session)
    return await service.generate_system_report()


@router.get(
    "/reports/child/{child_id}",
    response_model=ChildReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get child report",
    description=(
        "Returns a comprehensive report for a child including "
        "profile, guardian information, rescue history, incidents, "
        "timeline summary, and reunion status."
    ),
)
async def get_child_report(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> ChildReportResponse:
    """Generate a comprehensive child report."""
    service = ReportService(session)
    return await service.generate_child_report(child_id)


@router.get(
    "/reports/incident/{incident_analysis_id}",
    response_model=IncidentReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get incident analysis report",
    description=(
        "Returns a report for an incident analysis including "
        "AI description summary, severity, confidence scores, "
        "and recommendations."
    ),
)
async def get_incident_report(
    incident_analysis_id: str,
    session: AsyncSession = Depends(get_db),
) -> IncidentReportResponse:
    """Generate an incident analysis report."""
    service = ReportService(session)
    return await service.generate_incident_report(incident_analysis_id)


@router.get(
    "/reports/rescue/{rescue_session_id}",
    response_model=RescueReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get rescue session report",
    description=(
        "Returns a report for a rescue session including "
        "responder information, timeline, outcome, and duration."
    ),
)
async def get_rescue_report(
    rescue_session_id: str,
    session: AsyncSession = Depends(get_db),
) -> RescueReportResponse:
    """Generate a rescue session report."""
    service = ReportService(session)
    return await service.generate_rescue_report(rescue_session_id)


@router.get(
    "/reports/reunion/{reunion_record_id}",
    response_model=ReunionReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get reunion report",
    description=(
        "Returns a report for a reunion record including "
        "child and guardian information, verification status, "
        "and reunion summary."
    ),
)
async def get_reunion_report(
    reunion_record_id: str,
    session: AsyncSession = Depends(get_db),
) -> ReunionReportResponse:
    """Generate a reunion report."""
    service = ReportService(session)
    return await service.generate_reunion_report(reunion_record_id)