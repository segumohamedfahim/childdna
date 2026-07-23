"""Base Model with TimestampMixin for SQLAlchemy 2.0"""
from datetime import datetime
from uuid import UUID as uuid_UUID, uuid4
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps"""
    
    @declared_attr
    def id(cls) -> Mapped[uuid_UUID]:
        """UUID primary key - to be overridden in each model"""
        return mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SoftDeleteMixin(TimestampMixin):
    """Mixin for models that support soft delete"""
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
