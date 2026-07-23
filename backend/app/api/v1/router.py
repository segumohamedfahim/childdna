"""API v1 Router - Aggregates all API endpoints"""
from fastapi import APIRouter
from app.routers.system.health import router as health_router
from app.api.v1.endpoints.guardian import router as guardian_router
from app.api.v1.endpoints.child import router as child_router
from app.api.v1.endpoints.token import router as token_router
from app.api.v1.endpoints.qr_code import router as qr_router
from app.api.v1.endpoints.scanner import router as scanner_router
from app.api.v1.endpoints.rescue import router as rescue_router
from app.api.v1.endpoints.timeline import router as timeline_router
from app.api.v1.endpoints.reunion import router as reunion_router

api_router = APIRouter()

# Include system routers
api_router.include_router(health_router, prefix="/system")

# Include guardian and child routers
api_router.include_router(guardian_router)
api_router.include_router(child_router)
api_router.include_router(token_router)
api_router.include_router(qr_router)
api_router.include_router(scanner_router)
api_router.include_router(rescue_router)
api_router.include_router(timeline_router)
api_router.include_router(reunion_router)
