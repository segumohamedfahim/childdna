"""FastAPI Security Dependencies - For Future Authentication Injection"""
from typing import Annotated
from fastapi import Depends
from app.database.connection import get_db, AsyncSession

# Database dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]