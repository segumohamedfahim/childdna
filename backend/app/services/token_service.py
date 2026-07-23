"""Token Service - Business Logic for Child DNA Token Management"""
import secrets
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.child_token import ChildToken
from app.models.child import Child
from app.models.enums import TokenStatus
from app.schemas.child_token import ChildTokenResponse
from app.repositories.child_token import ChildTokenRepository
from app.repositories.child import ChildRepository
from app.core.exceptions import (
    TokenNotFound,
    TokenAlreadyActive,
    TokenAlreadyRevoked,
    TokenExpired,
    ChildAlreadyHasActiveToken,
    InvalidTokenFormat,
)
from app.utils.token_generator import generate, validate_format
from app.config.settings import settings


class TokenService:
    """Service for managing Child DNA tokens"""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ChildTokenRepository(session)
        self.child_repository = ChildRepository(session)
    
    async def generate_token(self, child_id: str) -> ChildTokenResponse:
        """Generate a new token for a child.
        
        Args:
            child_id: The ID of the child to generate a token for
            
        Returns:
            ChildTokenResponse: The newly created token
            
        Raises:
            ChildNotFound: If child does not exist
            ChildNotActive: If child is not active
            ChildAlreadyHasActiveToken: If child already has an active token
        """
        # Validate child exists and is active
        child = await self.child_repository.get_by_id(child_id)
        if not child:
            from app.core.exceptions import ChildNotFound
            raise ChildNotFound(child_id=child_id)
        
        if not child.is_active:
            from app.core.exceptions import ChildNotActive
            raise ChildNotActive(child_id=child_id)
        
        # Check for existing active token
        existing_token = await self.repository.get_active_by_child(child_id)
        if existing_token:
            raise ChildAlreadyHasActiveToken(child_id=child_id)
        
        # Generate unique token with retry mechanism
        token_code = await self._generate_unique_token()
        
        # Create token
        token = ChildToken(
            child_id=child_id,
            token_code=token_code,
            qr_secret=secrets.token_urlsafe(32),
            status=TokenStatus.ISSUED,
        )
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        
        return ChildTokenResponse.model_validate(token)
    
    async def _generate_unique_token(self) -> str:
        """Generate a unique token code with collision handling.
        
        Returns:
            str: A unique token code
        """
        for _ in range(settings.MAX_TOKEN_GENERATION_ATTEMPTS):
            token_code = generate()
            if not await self.repository.token_exists(token_code):
                return token_code
        
        # If all attempts fail, raise an error
        raise RuntimeError("Failed to generate unique token after maximum attempts")
    
    async def activate_token(self, token_code: str) -> ChildTokenResponse:
        """Activate a token.
        
        Args:
            token_code: The token code to activate
            
        Returns:
            ChildTokenResponse: The activated token
            
        Raises:
            InvalidTokenFormat: If token format is invalid
            TokenNotFound: If token does not exist
            TokenAlreadyActive: If token is already active
            TokenAlreadyRevoked: If token is already revoked
            TokenExpired: If token is expired
        """
        # Validate format
        if not validate_format(token_code):
            raise InvalidTokenFormat(token_code=token_code)
        
        # Get token
        token = await self.repository.get_by_token_code(token_code)
        if not token:
            raise TokenNotFound(token_code=token_code)
        
        # Check current status
        if token.status == TokenStatus.ACTIVE:
            raise TokenAlreadyActive(token_code=token_code)
        
        if token.status == TokenStatus.REVOKED:
            raise TokenAlreadyRevoked(token_code=token_code)
        
        if token.status == TokenStatus.EXPIRED:
            raise TokenExpired(token_code=token_code)
        
        # Activate token
        return ChildTokenResponse.model_validate(
            await self.repository.activate(token)
        )
    
    async def revoke_token(self, token_code: str) -> ChildTokenResponse:
        """Revoke a token.
        
        Args:
            token_code: The token code to revoke
            
        Returns:
            ChildTokenResponse: The revoked token
            
        Raises:
            InvalidTokenFormat: If token format is invalid
            TokenNotFound: If token does not exist
            TokenAlreadyRevoked: If token is already revoked
            TokenExpired: If token is expired
        """
        # Validate format
        if not validate_format(token_code):
            raise InvalidTokenFormat(token_code=token_code)
        
        # Get token
        token = await self.repository.get_by_token_code(token_code)
        if not token:
            raise TokenNotFound(token_code=token_code)
        
        # Check current status
        if token.status == TokenStatus.REVOKED:
            raise TokenAlreadyRevoked(token_code=token_code)
        
        if token.status == TokenStatus.EXPIRED:
            raise TokenExpired(token_code=token_code)
        
        # Revoke token
        return ChildTokenResponse.model_validate(
            await self.repository.revoke(token)
        )
    
    async def expire_token(self, token_code: str) -> ChildTokenResponse:
        """Expire a token.
        
        Args:
            token_code: The token code to expire
            
        Returns:
            ChildTokenResponse: The expired token
            
        Raises:
            InvalidTokenFormat: If token format is invalid
            TokenNotFound: If token does not exist
            TokenAlreadyRevoked: If token is already revoked
            TokenExpired: If token is already expired
        """
        # Validate format
        if not validate_format(token_code):
            raise InvalidTokenFormat(token_code=token_code)
        
        # Get token
        token = await self.repository.get_by_token_code(token_code)
        if not token:
            raise TokenNotFound(token_code=token_code)
        
        # Check current status
        if token.status == TokenStatus.REVOKED:
            raise TokenAlreadyRevoked(token_code=token_code)
        
        if token.status == TokenStatus.EXPIRED:
            raise TokenExpired(token_code=token_code)
        
        # Expire token
        return ChildTokenResponse.model_validate(
            await self.repository.expire(token)
        )
    
    async def get_child_tokens(self, child_id: str) -> list[ChildTokenResponse]:
        """Get all tokens for a child.
        
        Args:
            child_id: The ID of the child
            
        Returns:
            list[ChildTokenResponse]: List of tokens for the child
        """
        tokens = await self.repository.get_by_child(child_id)
        return [ChildTokenResponse.model_validate(t) for t in tokens]