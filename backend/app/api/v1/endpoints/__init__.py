"""API v1 Endpoints Package"""
from app.api.v1.endpoints.guardian import router as guardian_router
from app.api.v1.endpoints.child import router as child_router

__all__ = [
    "guardian_router",
    "child_router",
]