"""Child DNA Backend - FastAPI Application Entry Point"""
import uvicorn
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.core.exceptions import register_exception_handlers
from app.api.v1.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging import setup_logging
from app.config.settings import settings

# Create FastAPI application with lifespan events
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Setup middleware
setup_cors(app)
setup_logging(app)

# Setup security headers
from app.core.security_headers import setup_security_headers
setup_security_headers(app)

# Validate settings
settings.validate_settings()

# Register exception handlers
register_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
