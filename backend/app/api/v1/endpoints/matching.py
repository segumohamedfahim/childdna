"""Incident Matching API Endpoints - AI Match Recommendations"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.incident_matching_service import IncidentMatchingService
from app.schemas.incident_match import (
    MatchRequest,
    MatchListResponse,
    CompareRequest,
    CompareResponse,
)

router = APIRouter(tags=["matching"])


@router.post(
    "/rescue/incidents/{incident_id}/match",
    response_model=MatchListResponse,
    status_code=status.HTTP_200_OK,
    summary="Find potential matches for an incident",
    description=(
        "Runs the REUNITE Match engine on a rescue incident to find "
        "potential matches against other incidents. Returns ranked "
        "matches with similarity scores, categories, and "
        "recommendations. The AI only recommends; authorities always "
        "make the final merge decision."
    ),
)
async def match_incident(
    incident_id: str,
    request: MatchRequest,
    session: AsyncSession = Depends(get_db),
) -> MatchListResponse:
    """Find potential matches for a rescue incident.

    Args:
        incident_id: The incident UUID.
        request: Match request with optional candidate filter.
        session: Database session.

    Returns:
        MatchListResponse: Ranked potential matches.
    """
    service = IncidentMatchingService(session)
    return await service.find_matches(incident_id, request)


@router.get(
    "/rescue/incidents/{incident_id}/matches",
    response_model=MatchListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get stored matches for an incident",
    description=(
        "Retrieves previously computed match results for a rescue "
        "incident, ordered by similarity score descending."
    ),
)
async def get_incident_matches(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> MatchListResponse:
    """Get stored matches for an incident.

    Args:
        incident_id: The incident UUID.
        session: Database session.

    Returns:
        MatchListResponse: Stored matches ordered by similarity.
    """
    service = IncidentMatchingService(session)
    return await service.get_matches(incident_id)


@router.post(
    "/reunite/compare",
    response_model=CompareResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare two analyses",
    description=(
        "Compares two specific incident analyses without persisting "
        "results. Returns the similarity score, match category, "
        "and recommendation for the pair."
    ),
)
async def compare_analyses(
    request: CompareRequest,
    session: AsyncSession = Depends(get_db),
) -> CompareResponse:
    """Compare two analyses without persisting results.

    Args:
        request: Compare request with two incident IDs.
        session: Database session.

    Returns:
        CompareResponse: Comparison result.
    """
    service = IncidentMatchingService(session)
    return await service.compare(request)
