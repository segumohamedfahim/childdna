"""Incident Intelligence API Endpoints - AI Analysis"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.incident_intelligence_service import IncidentIntelligenceService
from app.schemas.incident_analysis import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["intelligence"])


@router.post(
    "/rescue/incidents/{incident_id}/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a rescue incident report",
    description=(
        "Runs the intelligence engine on a rescue report to extract "
        "structured attributes including gender, age, emotion, clothing, "
        "location, and distinguishing features with confidence scores."
    ),
)
async def analyze_incident(
    incident_id: str,
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """Analyze a rescue report and return structured intelligence."""
    service = IncidentIntelligenceService(session)
    return await service.analyze(incident_id, request)


@router.get(
    "/rescue/incidents/{incident_id}/analysis",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get incident analysis",
    description="Retrieves the stored intelligence analysis for an incident.",
)
async def get_incident_analysis(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """Get existing analysis for an incident."""
    service = IncidentIntelligenceService(session)
    return await service.get_analysis(incident_id)