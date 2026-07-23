"""Base Repository - Generic CRUD Operations"""
from typing import Optional, TypeVar, Generic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declared_attr

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository with common CRUD operations"""
    
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, entity_id) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all entities with pagination"""
        result = await self.session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, entity_data) -> ModelType:
        """Create a new entity"""
        entity = self.model(**entity_data.model_dump())
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, entity: ModelType, update_data) -> ModelType:
        """Update an entity"""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(entity, field, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity