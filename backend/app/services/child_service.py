"""Child Service - Business Logic for Child Operations"""
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.child import ChildRepository
from app.repositories.guardian import GuardianRepository
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse
from app.core.exceptions import (
    ChildNotFound,
    GuardianNotFound,
    GuardianNotActive,
    InvalidChildData,
)
from app.utils.logger import logger


class ChildService:
    """Service class for Child business logic"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.repository = ChildRepository(session)
        self.guardian_repository = GuardianRepository(session)
    
    async def create_child(self, child_data: ChildCreate) -> ChildResponse:
        """
        Create a new child.
        
        Args:
            child_data: Child creation data
            
        Returns:
            ChildResponse: Created child
            
        Raises:
            GuardianNotFound: If guardian not found
            GuardianNotActive: If guardian is not active
            InvalidChildData: If child data is invalid
        """
        # Validate guardian exists and is active
        guardian = await self.guardian_repository.get_by_id(child_data.guardian_id)
        if not guardian:
            logger.warning(f"Child creation failed: guardian {child_data.guardian_id} not found")
            raise GuardianNotFound(guardian_id=child_data.guardian_id)
        
        if not guardian.is_active:
            logger.warning(f"Child creation failed: guardian {child_data.guardian_id} not active")
            raise GuardianNotActive(guardian_id=child_data.guardian_id)
        
        # Validate date of birth is not in the future
        if child_data.date_of_birth > date.today():
            logger.warning("Child creation failed: date of birth in future")
            raise InvalidChildData(
                message="Date of birth cannot be in the future",
                details={"date_of_birth": str(child_data.date_of_birth)},
            )
        
        # Create child
        child = await self.repository.create(child_data)
        logger.info(f"Child created: id={child.id}, guardian_id={child_data.guardian_id}")
        
        return ChildResponse.model_validate(child)
    
    async def get_child(self, child_id: str) -> ChildResponse:
        """
        Get child by ID.
        
        Args:
            child_id: Child UUID
            
        Returns:
            ChildResponse: Child data
            
        Raises:
            ChildNotFound: If child not found
        """
        child = await self.repository.get_by_id(child_id)
        if not child:
            logger.warning(f"Child not found: id={child_id}")
            raise ChildNotFound(child_id=child_id)
        
        return ChildResponse.model_validate(child)
    
    async def list_children(self, skip: int = 0, limit: int = 100) -> list[ChildResponse]:
        """
        Get all children with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            list[ChildResponse]: List of children
        """
        children = await self.repository.get_all(skip=skip, limit=limit)
        return [ChildResponse.model_validate(child) for child in children]
    
    async def update_child(
        self, child_id: str, update_data: ChildUpdate
    ) -> ChildResponse:
        """
        Update child information.
        
        Args:
            child_id: Child UUID
            update_data: Child update data
            
        Returns:
            ChildResponse: Updated child
            
        Raises:
            ChildNotFound: If child not found
            InvalidChildData: If child data is invalid
        """
        child = await self.repository.get_by_id(child_id)
        if not child:
            logger.warning(f"Child not found for update: id={child_id}")
            raise ChildNotFound(child_id=child_id)
        
        # Validate date of birth if provided
        if update_data.date_of_birth and update_data.date_of_birth > date.today():
            logger.warning("Child update failed: date of birth in future")
            raise InvalidChildData(
                message="Date of birth cannot be in the future",
                details={"date_of_birth": str(update_data.date_of_birth)},
            )
        
        updated_child = await self.repository.update(child, update_data)
        logger.info(f"Child updated: id={child_id}")
        
        return ChildResponse.model_validate(updated_child)
    
    async def validate_guardian_exists(self, guardian_id: str) -> bool:
        """
        Check if guardian exists and is active.
        
        Args:
            guardian_id: Guardian UUID
            
        Returns:
            bool: True if guardian exists and is active
            
        Raises:
            GuardianNotFound: If guardian not found
            GuardianNotActive: If guardian is not active
        """
        guardian = await self.guardian_repository.get_by_id(guardian_id)
        if not guardian:
            raise GuardianNotFound(guardian_id=guardian_id)
        
        if not guardian.is_active:
            raise GuardianNotActive(guardian_id=guardian_id)
        
        return True