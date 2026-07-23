"""SQLAlchemy Declarative Base - For Future Model Definitions"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

__all__ = ["Base"]
