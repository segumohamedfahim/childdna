"""Guardian Service - Business Logic for Guardian Operations"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.guardian import GuardianRepository
from app.schemas.guardian import GuardianCreate, GuardianUpdate, GuardianResponse
from app.core.exceptions import (
    GuardianAlreadyExists,
    GuardianNotFound,
    InvalidGuardianData,
)
from app.utils.logger import logger


class GuardianService:
    """Service class for Guardian business logic"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.repository = GuardianRepository(session)
    
    async def create_guardian(self, guardian_data: GuardianCreate) -> GuardianResponse:
        """
        Create a new guardian.
        
        Args:
            guardian_data: Guardian creation data
            
        Returns:
            GuardianResponse: Created guardian
            
        Raises:
            GuardianAlreadyExists: If email already exists
        """
        # Check if email already exists
        existing_guardian = await self.repository.get_by_email(guardian_data.email)
        if existing_guardian:
            logger.warning(f"Guardian creation failed: email {guardian_data.email} already exists")
            raise GuardianAlreadyExists(email=guardian_data.email)
        
        # Create guardian
        guardian = await self.repository.create(guardian_data)
        logger.info(f"Guardian created: id={guardian.id}")
        
        return GuardianResponse.model_validate(guardian)
    
    async def get_guardian(self, guardian_id: str) -> GuardianResponse:
        """
        Get guardian by ID.
        
        Args:
            guardian_id: Guardian UUID
            
        Returns:
            GuardianResponse: Guardian data
            
        Raises:
            GuardianNotFound: If guardian not found
        """
        guardian = await self.repository.get_by_id(guardian_id)
        if not guardian:
            logger.warning(f"Guardian not found: id={guardian_id}")
            raise GuardianNotFound(guardian_id=guardian_id)
        
        return GuardianResponse.model_validate(guardian)
    
    async def get_guardian_by_email(self, email: str) -> GuardianResponse:
        """
        Get guardian by email.
        
        Args:
            email: Guardian email
            
        Returns:
            GuardianResponse: Guardian data
            
        Raises:
            GuardianNotFound: If guardian not found
        """
        guardian = await self.repository.get_by_email(email)
        if not guardian:
            logger.warning(f"Guardian not found: email={email}")
            raise GuardianNotFound(guardian_id=email)
        
        return GuardianResponse.model_validate(guardian)
    
    async def update_guardian(
        self, guardian_id: str, update_data: GuardianUpdate
    ) -> GuardianResponse:
        """
        Update guardian information.
        
        Args:
            guardian_id: Guardian UUID
            update_data: Guardian update data
            
        Returns:
            GuardianResponse: Updated guardian
            
        Raises:
            GuardianNotFound: If guardian not found
        """
        guardian = await self.repository.get_by_id(guardian_id)
        if not guardian:
            logger.warning(f"Guardian not found for update: id={guardian_id}")
            raise GuardianNotFound(guardian_id=guardian_id)
        
        updated_guardian = await self.repository.update(guardian, update_data)
        logger.info(f"Guardian updated: id={guardian_id}")
        
        return GuardianResponse.model_validate(updated_guardian)
    
    async def deactivate_guardian(self, guardian_id: str) -> None:
        """
        Soft delete a guardian.
        
        Args:
            guardian_id: Guardian UUID
            
        Raises:
            GuardianNotFound: If guardian not found
        """
        guardian = await self.repository.get_by_id(guardian_id)
        if not guardian:
            logger.warning(f"Guardian not found for deactivation: id={guardian_id}")
            raise GuardianNotFound(guardian_id=guardian_id)
        
        await self.repository.delete(guardian)
        logger.info(f"Guardian deactivated: id={guardian_id}")
    
    async def list_guardian_children(self, guardian_id: str) -> list[GuardianResponse]:
        """
        Get all children for a guardian.
        
        Args:
            guardian_id: Guardian UUID
            
        Returns:
            list[GuardianResponse]: List of children
            
        Raises:
            GuardianNotFound: If guardian not found
        """
        guardian = await self.repository.get_by_id(guardian_id)
        if not guardian:
            logger.warning(f"Guardian not found for children list: id={guardian_id}")
            raise GuardianNotFound(guardian_id=guardian_id)
        
        return [GuardianResponse.model_validate(child) for child in guardian.children]