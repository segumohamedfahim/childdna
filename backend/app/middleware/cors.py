"""CORS Middleware Configuration"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the application"""
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )