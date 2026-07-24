"""Pytest Configuration and Fixtures"""
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.jwt_service import JWTService


@pytest.fixture
def client():
    """Test client fixture for API testing with auth disabled."""
    import app.api.dependencies.auth as auth_deps
    from app.models.user import User

    mock_user = MagicMock(spec=User)
    mock_user.id = "test-user-id"
    mock_user.email = "test@example.com"
    mock_user.full_name = "Test User"
    mock_user.role = "admin"
    mock_user.is_active = True

    async def mock_oauth():
        return "test-token"

    async def mock_get_user():
        return mock_user

    async def mock_optional_user():
        return mock_user

    # Override auth dependencies to bypass JWT/role checking
    app.dependency_overrides[auth_deps.oauth2_scheme] = mock_oauth
    app.dependency_overrides[auth_deps.get_current_user] = mock_get_user
    app.dependency_overrides[auth_deps.get_optional_user] = mock_optional_user

    yield TestClient(app)

    # Clean up
    app.dependency_overrides = {}


@pytest.fixture
def admin_token() -> str:
    """Generate a valid admin JWT token for testing protected endpoints."""
    jwt_service = JWTService()
    return jwt_service.create_access_token(
        user_id="admin-test-id",
        role="admin",
    )


@pytest.fixture
def admin_auth_header(admin_token: str) -> dict:
    """Authorization header with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def authority_token() -> str:
    """Generate a valid authority JWT token."""
    jwt_service = JWTService()
    return jwt_service.create_access_token(
        user_id="authority-test-id",
        role="authority",
    )


@pytest.fixture
def authority_auth_header(authority_token: str) -> dict:
    """Authorization header with authority token."""
    return {"Authorization": f"Bearer {authority_token}"}


@pytest.fixture
def guardian_token() -> str:
    """Generate a valid guardian JWT token."""
    jwt_service = JWTService()
    return jwt_service.create_access_token(
        user_id="guardian-test-id",
        role="guardian",
    )


@pytest.fixture
def guardian_auth_header(guardian_token: str) -> dict:
    """Authorization header with guardian token."""
    return {"Authorization": f"Bearer {guardian_token}"}


@pytest.fixture
def scanner_token() -> str:
    """Generate a valid scanner JWT token."""
    jwt_service = JWTService()
    return jwt_service.create_access_token(
        user_id="scanner-test-id",
        role="scanner",
    )


@pytest.fixture
def scanner_auth_header(scanner_token: str) -> dict:
    """Authorization header with scanner token."""
    return {"Authorization": f"Bearer {scanner_token}"}