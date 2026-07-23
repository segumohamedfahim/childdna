"""FastAPI Lifespan Events - Application Startup and Shutdown"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.database.connection import init_db, close_db
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Child DNA Backend...")
    try:
        await init_db()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.warning(f"Database not available, starting without DB: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Child DNA Backend...")
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.warning(f"Error closing database: {e}")
