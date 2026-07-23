"""Child API Endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.child_service import ChildService
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse
from app.database.connection import get_db

router = APIRouter(tags=["children"])


async def get_child_service(
    session: AsyncSession = Depends(get_db),
) -> ChildService:
    """Dependency for ChildService"""
    return ChildService(session)


@router.post(
    "/children",
    response_model=ChildResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new child",
    description="Register a new child under an existing guardian",
)
async def create_child(
    child_data: ChildCreate,
    service: ChildService = Depends(get_child_service),
) -> ChildResponse:
    """Create a new child"""
    return await service.create_child(child_data)


@router.get(
    "/children/{child_id}",
    response_model=ChildResponse,
    status_code=status.HTTP_200_OK,
    summary="Get child by ID",
    description="Retrieve a child's information by their unique identifier",
)
async def get_child(
    child_id: str,
    service: ChildService = Depends(get_child_service),
) -> ChildResponse:
    """Get child by ID"""
    return await service.get_child(child_id)


@router.put(
    "/children/{child_id}",
    response_model=ChildResponse,
    status_code=status.HTTP_200_OK,
    summary="Update child information",
    description="Update a child's information by their unique identifier",
)
async def update_child(
    child_id: str,
    update_data: ChildUpdate,
    service: ChildService = Depends(get_child_service),
) -> ChildResponse:
    """Update child information"""
    return await service.update_child(child_id, update_data)