"""Prediction API Endpoints - AI Intelligence & Predictions"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.prediction_service import PredictionService
from app.schemas.prediction import (
    ReunionPredictionResponse,
    RescuePredictionResponse,
    IncidentRiskResponse,
    AlertPredictionResponse,
    PriorityPredictionResponse,
    AISummaryResponse,
    RecommendationResponse,
    PredictionHealthResponse,
)

router = APIRouter(tags=["prediction"])


@router.get(
    "/prediction/reunion/{child_id}",
    response_model=ReunionPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict reunion probability",
    description="Predicts the probability of a child being reunited based on heuristic analysis.",
)
async def predict_reunion(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> ReunionPredictionResponse:
    """Predict reunion probability for a child."""
    service = PredictionService(session)
    return await service.predict_reunion_probability(child_id)


@router.get(
    "/prediction/rescue/{session_id}",
    response_model=RescuePredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict rescue success",
    description="Predicts rescue session success probability based on status and context.",
)
async def predict_rescue(
    session_id: str,
    session: AsyncSession = Depends(get_db),
) -> RescuePredictionResponse:
    """Predict rescue session success."""
    service = PredictionService(session)
    return await service.predict_rescue_success(session_id)


@router.get(
    "/prediction/risk/{child_id}",
    response_model=IncidentRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict incident risk",
    description="Assesses incident risk level for a child based on history and status.",
)
async def predict_risk(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> IncidentRiskResponse:
    """Assess incident risk for a child."""
    service = PredictionService(session)
    return await service.predict_incident_risk(child_id)


@router.get(
    "/prediction/alert/{analysis_id}",
    response_model=AlertPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict alert probability",
    description="Predicts the probability of an alert being generated for an analysis.",
)
async def predict_alert(
    analysis_id: str,
    session: AsyncSession = Depends(get_db),
) -> AlertPredictionResponse:
    """Predict alert probability for an analysis."""
    service = PredictionService(session)
    return await service.predict_alert_probability(analysis_id)


@router.get(
    "/prediction/priority/{analysis_id}",
    response_model=PriorityPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate priority score",
    description="Generates a priority score for an incident analysis.",
)
async def get_priority(
    analysis_id: str,
    session: AsyncSession = Depends(get_db),
) -> PriorityPredictionResponse:
    """Generate priority score for an analysis."""
    service = PredictionService(session)
    return await service.generate_priority_score(analysis_id)


@router.get(
    "/prediction/summary/{summary_type}/{entity_id}",
    response_model=AISummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI summary",
    description="Generates a structured AI summary for an entity (child, incident, rescue, guardian, reunion).",
)
async def get_ai_summary(
    summary_type: str,
    entity_id: str,
    session: AsyncSession = Depends(get_db),
) -> AISummaryResponse:
    """Generate a structured AI summary."""
    service = PredictionService(session)
    return await service.generate_ai_summary(entity_id, summary_type)


@router.get(
    "/prediction/recommendations/{entity_type}/{entity_id}",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recommendations",
    description="Returns rule-based recommendations for an entity.",
)
async def get_recommendations(
    entity_type: str,
    entity_id: str,
    session: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Get recommendations for an entity."""
    service = PredictionService(session)
    return await service.generate_recommendations(entity_id, entity_type)


@router.get(
    "/prediction/health",
    response_model=PredictionHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get prediction health",
    description="Returns the health status of the prediction AI platform.",
)
async def get_prediction_health(
    session: AsyncSession = Depends(get_db),
) -> PredictionHealthResponse:
    """Get prediction health status."""
    service = PredictionService(session)
    return await service.get_prediction_health()