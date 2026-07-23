"""JWT Token Utilities - Token Creation, Verification, and Decoding"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from app.config.settings import settings


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token"""
    expire = datetime.utcnow() + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {"exp": expire, "sub": subject, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str) -> bool:
    """Verify a JWT token is valid"""
    try:
        jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return True
    except JWTError:
        return False


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """Decode a JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None