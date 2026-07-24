"""Incident Matching Service - AI Match Orchestration"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rescue_session import RescueSessionRepository
from app.repositories.incident_analysis import IncidentAnalysisRepository
from app.repositories.incident_match import IncidentMatchRepository
from app.schemas.incident_match import (
    MatchRequest,
    MatchListResponse,
    MatchResponse,
    CompareRequest,
    CompareResponse,
)
from app.schemas.incident_analysis import AnalyzeResponse
from app.core.exceptions import (
    RescueSessionNotFound,
    AnalysisNotFound,
)
from app.ai.matching_engine import find_matches as run_matching
from app.utils.logger import logger


class IncidentMatchingService:
    """Service for incident matching.

    Orchestrates the matching pipeline: validates the incident,
    loads the source analysis, loads candidate analyses, runs
    the AI matching engine, persists results, and returns ranked
    matches.

    The AI only recommends; authorities always make the final
    merge decision.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.rescue_repo = RescueSessionRepository(session)
        self.analysis_repo = IncidentAnalysisRepository(session)
        self.match_repo = IncidentMatchRepository(session)

    async def find_matches(
        self, incident_id: str, request: MatchRequest,
    ) -> MatchListResponse:
        """Find potential matches for a rescue incident.

        Validates the incident exists, loads the source analysis,
        loads candidate analyses, runs the AI matching engine,
        persists results, and returns ranked matches.

        Args:
            incident_id: The source incident UUID.
            request: Match request with optional candidate filter.

        Returns:
            MatchListResponse: Ranked potential matches.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
            AnalysisNotFound: If the incident has no analysis.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Load source analysis
        source_analysis = await self.analysis_repo.get_by_incident(
            incident_id
        )
        if not source_analysis:
            raise AnalysisNotFound(incident_id=incident_id)

        # Load candidate analyses
        candidate_dicts = await self._load_candidates(
            incident_id, request
        )

        if not candidate_dicts:
            return MatchListResponse(
                incident_id=incident_id,
                matches=[],
                total_matches=0,
                algorithm_version="rule_engine_v1",
            )

        # Convert source analysis to dict
        source_dict = self._analysis_to_dict(source_analysis)

        # Run the AI matching engine (stateless, pure function)
        match_results = run_matching(source_dict, candidate_dicts)

        # Build persistence data
        match_data = [
            {
                "incident_id": incident_id,
                "matched_incident_id": result.matched_incident_id,
                "similarity_score": result.similarity_score,
                "match_category": result.match_category,
                "recommendation": result.recommendation,
                "algorithm_version": "rule_engine_v1",
                "score_breakdown": result.score_breakdown,
            }
            for result in match_results
        ]

        # Delete existing matches for this incident (prevent duplicates)
        await self.match_repo.delete_matches(incident_id)

        # Persist matches via repository
        if match_data:
            await self.match_repo.create_many(match_data)

        # Build response
        matches = [
            MatchResponse(
                matched_incident_id=result.matched_incident_id,
                similarity_score=result.similarity_score,
                match_category=result.match_category,
                recommendation=result.recommendation,
                score_breakdown=result.score_breakdown,
                algorithm_version="rule_engine_v1",
            )
            for result in match_results
        ]

        logger.info(
            f"Incident matching completed: incident_id={incident_id}, "
            f"matches_found={len(matches)}"
        )

        return MatchListResponse(
            incident_id=incident_id,
            matches=matches,
            total_matches=len(matches),
            algorithm_version="rule_engine_v1",
        )

    async def get_matches(
        self, incident_id: str, limit: int = 20,
    ) -> MatchListResponse:
        """Get stored matches for an incident.

        Args:
            incident_id: The incident UUID.
            limit: Maximum number of matches to return.

        Returns:
            MatchListResponse: Stored matches ordered by similarity.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        # Fetch stored matches
        stored_matches = await self.match_repo.get_top_matches(
            incident_id, limit
        )

        matches = [
            MatchResponse.model_validate(m) for m in stored_matches
        ]

        return MatchListResponse(
            incident_id=incident_id,
            matches=matches,
            total_matches=len(matches),
            algorithm_version="rule_engine_v1",
        )

    async def compare(
        self, request: CompareRequest,
    ) -> CompareResponse:
        """Compare two analyses without persisting results.

        Args:
            request: Compare request with two incident IDs.

        Returns:
            CompareResponse: Comparison result.

        Raises:
            RescueSessionNotFound: If either incident does not exist.
            AnalysisNotFound: If either incident has no analysis.
        """
        # Validate both incidents exist
        incident_a = await self.rescue_repo.get_by_id(
            request.incident_id_a
        )
        if not incident_a:
            raise RescueSessionNotFound(
                incident_id=request.incident_id_a
            )

        incident_b = await self.rescue_repo.get_by_id(
            request.incident_id_b
        )
        if not incident_b:
            raise RescueSessionNotFound(
                incident_id=request.incident_id_b
            )

        # Load both analyses
        analysis_a = await self.analysis_repo.get_by_incident(
            request.incident_id_a
        )
        if not analysis_a:
            raise AnalysisNotFound(
                incident_id=request.incident_id_a
            )

        analysis_b = await self.analysis_repo.get_by_incident(
            request.incident_id_b
        )
        if not analysis_b:
            raise AnalysisNotFound(
                incident_id=request.incident_id_b
            )

        # Convert to dicts
        source_dict = self._analysis_to_dict(analysis_a)
        candidate_dict = self._analysis_to_dict(analysis_b)

        # Run matching engine with single candidate
        match_results = run_matching(source_dict, [candidate_dict])

        if not match_results:
            return CompareResponse(
                incident_id_a=request.incident_id_a,
                incident_id_b=request.incident_id_b,
                similarity_score=0.0,
                match_category="no_match",
                recommendation="no_action",
                score_breakdown={},
                algorithm_version="rule_engine_v1",
            )

        result = match_results[0]

        return CompareResponse(
            incident_id_a=request.incident_id_a,
            incident_id_b=request.incident_id_b,
            similarity_score=result.similarity_score,
            match_category=result.match_category,
            recommendation=result.recommendation,
            score_breakdown=result.score_breakdown,
            algorithm_version="rule_engine_v1",
        )

    async def delete_matches(self, incident_id: str) -> None:
        """Delete all matches for an incident.

        Args:
            incident_id: The incident UUID.

        Raises:
            RescueSessionNotFound: If the incident does not exist.
        """
        # Validate incident exists
        incident = await self.rescue_repo.get_by_id(incident_id)
        if not incident:
            raise RescueSessionNotFound(incident_id=incident_id)

        await self.match_repo.delete_matches(incident_id)

        logger.info(
            f"Matches deleted: incident_id={incident_id}"
        )

    async def _load_candidates(
        self, incident_id: str, request: MatchRequest,
    ) -> list[dict]:
        """Load candidate analyses as dicts.

        If candidate_incident_ids is provided, load only those.
        Otherwise, load all other incidents that have analyses.

        Args:
            incident_id: The source incident UUID.
            request: Match request with optional candidate filter.

        Returns:
            list[dict]: Candidate analysis dicts.
        """
        if request.candidate_incident_ids:
            candidates = []
            for candidate_id in request.candidate_incident_ids:
                if candidate_id == incident_id:
                    continue
                analysis = await self.analysis_repo.get_by_incident(
                    candidate_id
                )
                if analysis:
                    candidates.append(self._analysis_to_dict(analysis))
            return candidates

        # Load all analyses and filter out the source
        all_analyses = await self.analysis_repo.get_all()
        candidates = []
        for analysis in all_analyses:
            if analysis.incident_id == incident_id:
                continue
            candidates.append(self._analysis_to_dict(analysis))
        return candidates

    def _analysis_to_dict(
        self, analysis,
    ) -> dict:
        """Convert an IncidentAnalysis model to a dict for the engine.

        Args:
            analysis: The IncidentAnalysis model instance.

        Returns:
            dict: Analysis data as a dictionary.
        """
        response = AnalyzeResponse.model_validate(analysis)
        return response.model_dump()
