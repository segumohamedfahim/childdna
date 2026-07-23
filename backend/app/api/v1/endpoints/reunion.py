"""Reunion API Endpoints - Reunion Record Management"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.reunion_service import ReunionService
from app.schemas.reunion_record import (
    ReunionRecordCreate,
    ReunionRecordResponse,
)

router = APIRouter(tags=["reunion"])


@router.post(
    "/rescue/incidents/{incident_id}/reunion",
    response_model=ReunionRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a reunion",
    description=(
        "Records a child reunion with their guardian. The incident "
        "must be in ACTIVE status. Automatically generates a "
        "REUNION_COMPLETED timeline event and marks the incident "
        "as COMPLETE."
    ),
)
async def record_reunion(
    incident_id: str,
    reunion_data: ReunionRecordCreate,
    session: AsyncSession = Depends(get_db),
) -> ReunionRecordResponse:
    """Record a reunion and close the rescue incident.

    Args:
        incident_id: The incident UUID.
        reunion_data: Reunion record creation data.
        session: Database session.

    Returns:
        ReunionRecordResponse: The created reunion record.
    """
    service = ReunionService(session)
    return await service.record_reunion(incident_id, reunion_data)


@router.get(
    "/children/{child_id}/reunions",
    response_model=list[ReunionRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="List reunions for a child",
    description="Retrieves all reunion records associated with a child.",
)
async def get_child_reunions(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> list[ReunionRecordResponse]:
    """Get all reunion records for a child.

    Args:
        child_id: The child UUID.
        session: Database session.

    Returns:
        list[ReunionRecordResponse]: List of reunion records.
    """
    service = ReunionService(session)
    return await service.get_child_reunions(child_id)