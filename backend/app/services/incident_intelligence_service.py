"""Incident Intelligence Service - AI Analysis Orchestration"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.incident_analysis import IncidentAnalysisRepository
from app.schemas.incident_analysis import AnalyzeRequest, AnalyzeResponse
from app.core.exceptions import (
    RescueSessionNotFound,
)
from app.ai.incident_analyzer import analyze as run_analysis
from app.utils.logger import logger


class IncidentIntelligenceService:
    """Service for incident intelligence analysis.

    Orchestrates the analysis pipeline: validates the incident,
    runs the AI analyzer, persists results, and returns structured
    intelligence data.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rescue_repo = RescueSessionRepository(session)
        self.analysis_repo = IncidentAnalysisRepository(session)

    async def analyze(
        self, incident_id: str, request: AnalyzeRequest,
    ) -> AnalyzeResponse:
        """Analyze a rescue report and return structured intelligence.

        Validates the incident exists, runs the AI analyzer, persists
        the results, and returns structured attributes with confidence
        scores.

        Args:
            incident_id: The rescue session UUID.
            request: Analysis request containing the report text.

        Returns:
            AnalyzeResponse: Structured analysis with confidence scores.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Run the AI analyzer (stateless, pure function)
        analysis_result = run_analysis(request.notes)

        # Build persistence data
        analysis_data = {
            "incident_id": incident_id,
            "raw_text": request.notes,
            "analysis_engine": "rule_engine_v1",
            **analysis_result,
        }

        # Persist analysis via repository
        analysis = await self.analysis_repo.create_from_dict(analysis_data)

        logger.info(
            f"Incident analyzed: incident_id={incident_id}, "
            f"engine=rule_engine_v1, "
            f"confidence={analysis_result['overall_confidence']}"
        )

        return AnalyzeResponse.model_validate(analysis)

    async def get_analysis(
        self, incident_id: str,
    ) -> AnalyzeResponse:
        """Get existing analysis for an incident.

        Args:
            incident_id: The rescue session UUID.

        Returns:
            AnalyzeResponse: The stored analysis.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Fetch analysis
        analysis = await self.analysis_repo.get_by_incident(incident_id)
        if not analysis:
            from app.core.exceptions import AnalysisNotFound
            raise AnalysisNotFound(incident_id=incident_id)

        return AnalyzeResponse.model_validate(analysis)