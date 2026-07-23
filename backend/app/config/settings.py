"""Application Settings - Pydantic Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Application
    APP_NAME: str = "Child DNA API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:fahim2007@localhost:5432/child_dna"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-min-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Token Generation
    TOKEN_PREFIX: str = "DNA"
    TOKEN_SEPARATOR: str = "-"
    TOKEN_SEGMENT_LENGTH: int = 4
    MAX_TOKEN_GENERATION_ATTEMPTS: int = 3
    
    # QR Code Generation
    DEFAULT_QR_SIZE: int = 300
    MIN_QR_SIZE: int = 50
    MAX_QR_SIZE: int = 2000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()