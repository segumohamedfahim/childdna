"""Rescue Incident API Endpoints"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.services.rescue_service import RescueService
from app.schemas.rescue_session import (
    RescueSessionCreate,
    RescueSessionUpdate,
    RescueSessionResponse,
)

router = APIRouter(tags=["rescue"])


@router.post(
    "/rescue/incidents",
    response_model=RescueSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a rescue incident",
    description=(
        "Creates a new rescue incident for a child. The child must "
        "exist and must not already have an active incident. "
        "Automatically generates an INCIDENT_CREATED timeline event."
    ),
)
async def create_incident(
    incident_data: RescueSessionCreate,
    session: AsyncSession = Depends(get_db),
) -> RescueSessionResponse:
    """Create a new rescue incident."""
    service = RescueService(session)
    return await service.create_incident(incident_data)


@router.get(
    "/rescue/incidents",
    response_model=list[RescueSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all rescue incidents",
    description="Retrieves a paginated list of all rescue incidents.",
)
async def list_incidents(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum records to return"),
    session: AsyncSession = Depends(get_db),
) -> list[RescueSessionResponse]:
    """List all rescue incidents with pagination."""
    service = RescueService(session)
    return await service.list_incidents(skip=skip, limit=limit)


@router.get(
    "/rescue/incidents/{incident_id}",
    response_model=RescueSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a rescue incident",
    description="Retrieves a rescue incident by its unique identifier.",
)
async def get_incident(
    incident_id: str,
    session: AsyncSession = Depends(get_db),
) -> RescueSessionResponse:
    """Get a rescue incident by ID."""
    service = RescueService(session)
    return await service.get_incident(incident_id)


@router.patch(
    "/rescue/incidents/{incident_id}",
    response_model=RescueSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a rescue incident",
    description=(
        "Updates a rescue incident. Supports status transitions "
        "(PENDING->ACTIVE, ACTIVE->COMPLETE, PENDING/ACTIVE->CANCELLED) "
        "and field updates. Automatically generates STATUS_CHANGED "
        "and LOCATION_UPDATED timeline events."
    ),
)
async def update_incident(
    incident_id: str,
    update_data: RescueSessionUpdate,
    session: AsyncSession = Depends(get_db),
) -> RescueSessionResponse:
    """Update a rescue incident."""
    service = RescueService(session)
    return await service.update_incident(incident_id, update_data)


@router.get(
    "/children/{child_id}/incidents",
    response_model=list[RescueSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List incidents for a child",
    description="Retrieves all rescue incidents associated with a child.",
)
async def get_child_incidents(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> list[RescueSessionResponse]:
    """Get all incidents for a child."""
    service = RescueService(session)
    return await service.get_child_incidents(child_id)