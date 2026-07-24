"""Security Headers Middleware - HTTP Security Response Headers"""
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds security-related HTTP response headers.

    Adds headers to prevent common web vulnerabilities:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Restricts browser features
    - X-XSS-Protection: Enables XSS filter
    - Strict-Transport-Security: Enforces HTTPS (production only)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Control referrer information
        response.headers["Referrer-Policy"] = "no-referrer"

        # Restrict browser features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "interest-cohort=()"
        )

        # Enable XSS filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict-Transport-Security only in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


def setup_security_headers(app: FastAPI) -> None:
    """Configure security headers middleware for the application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(SecurityHeadersMiddleware)