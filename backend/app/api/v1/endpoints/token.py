"""Token API Endpoints - Child DNA Token Management"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.token_service import TokenService
from app.schemas.child_token import ChildTokenResponse
from app.database.connection import get_db

router = APIRouter(tags=["tokens"])


@router.post(
    "/children/{child_id}/tokens",
    response_model=ChildTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new token for a child",
    description="Creates a new Child DNA token for the specified child. The child must be active and not have an existing active token.",
)
async def create_token(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> ChildTokenResponse:
    """Generate a new token for a child.
    
    Args:
        child_id: The ID of the child to generate a token for
        session: Database session
        
    Returns:
        ChildTokenResponse: The newly created token
    """
    service = TokenService(session)
    return await service.generate_token(child_id)


@router.get(
    "/children/{child_id}/tokens",
    response_model=list[ChildTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tokens for a child",
    description="Retrieves all tokens associated with the specified child.",
)
async def list_child_tokens(
    child_id: str,
    session: AsyncSession = Depends(get_db),
) -> list[ChildTokenResponse]:
    """List all tokens for a child.
    
    Args:
        child_id: The ID of the child
        session: Database session
        
    Returns:
        list[ChildTokenResponse]: List of tokens for the child
    """
    service = TokenService(session)
    return await service.get_child_tokens(child_id)


@router.post(
    "/tokens/{token_code}/activate",
    response_model=ChildTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate a token",
    description="Activates a token for use. The token must be in ISSUED status.",
)
async def activate_token(
    token_code: str,
    session: AsyncSession = Depends(get_db),
) -> ChildTokenResponse:
    """Activate a token.
    
    Args:
        token_code: The token code to activate
        session: Database session
        
    Returns:
        ChildTokenResponse: The activated token
    """
    service = TokenService(session)
    return await service.activate_token(token_code)


@router.post(
    "/tokens/{token_code}/revoke",
    response_model=ChildTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke a token",
    description="Revokes a token. The token must be in ACTIVE or ISSUED status.",
)
async def revoke_token(
    token_code: str,
    session: AsyncSession = Depends(get_db),
) -> ChildTokenResponse:
    """Revoke a token.
    
    Args:
        token_code: The token code to revoke
        session: Database session
        
    Returns:
        ChildTokenResponse: The revoked token
    """
    service = TokenService(session)
    return await service.revoke_token(token_code)
