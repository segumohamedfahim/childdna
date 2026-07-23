"""Health Check Endpoint - System Status"""
from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    environment: str


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns system status and version information.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment="development",
    )