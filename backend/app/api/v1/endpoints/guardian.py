"""Guardian API Endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.guardian_service import GuardianService
from app.schemas.guardian import GuardianCreate, GuardianUpdate, GuardianResponse
from app.database.connection import get_db

router = APIRouter(tags=["guardians"])


async def get_guardian_service(
    session: AsyncSession = Depends(get_db),
) -> GuardianService:
    """Dependency for GuardianService"""
    return GuardianService(session)


@router.post(
    "/guardians",
    response_model=GuardianResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new guardian",
    description="Register a new guardian with email, phone, and address information",
)
async def create_guardian(
    guardian_data: GuardianCreate,
    service: GuardianService = Depends(get_guardian_service),
) -> GuardianResponse:
    """Create a new guardian"""
    return await service.create_guardian(guardian_data)


@router.get(
    "/guardians/{guardian_id}",
    response_model=GuardianResponse,
    status_code=status.HTTP_200_OK,
    summary="Get guardian by ID",
    description="Retrieve a guardian's information by their unique identifier",
)
async def get_guardian(
    guardian_id: str,
    service: GuardianService = Depends(get_guardian_service),
) -> GuardianResponse:
    """Get guardian by ID"""
    return await service.get_guardian(guardian_id)


@router.put(
    "/guardians/{guardian_id}",
    response_model=GuardianResponse,
    status_code=status.HTTP_200_OK,
    summary="Update guardian information",
    description="Update a guardian's information by their unique identifier",
)
async def update_guardian(
    guardian_id: str,
    update_data: GuardianUpdate,
    service: GuardianService = Depends(get_guardian_service),
) -> GuardianResponse:
    """Update guardian information"""
    return await service.update_guardian(guardian_id, update_data)


@router.delete(
    "/guardians/{guardian_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a guardian",
    description="Soft delete a guardian by their unique identifier",
)
async def deactivate_guardian(
    guardian_id: str,
    service: GuardianService = Depends(get_guardian_service),
) -> None:
    """Deactivate a guardian"""
    await service.deactivate_guardian(guardian_id)


@router.get(
    "/guardians/{guardian_id}/children",
    response_model=list[GuardianResponse],
    status_code=status.HTTP_200_OK,
    summary="Get guardian's children",
    description="Retrieve all children registered under a guardian",
)
async def get_guardian_children(
    guardian_id: str,
    service: GuardianService = Depends(get_guardian_service),
) -> list[GuardianResponse]:
    """Get all children for a guardian"""
    return await service.list_guardian_children(guardian_id)