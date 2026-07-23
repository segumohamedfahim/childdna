"""Custom Exceptions for Child DNA API"""
from typing import Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class GuardianAlreadyExists(HTTPException):
    """Exception raised when guardian email already exists"""
    
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=409,
            detail={
                "success": False,
                "message": "Guardian with this email already exists",
                "error_code": "GUARDIAN_ALREADY_EXISTS",
                "details": None,
            },
        )


class GuardianNotFound(HTTPException):
    """Exception raised when guardian is not found"""
    
    def __init__(self, guardian_id: str) -> None:
        super().__init__(
            status_code=404,
            detail={
                "success": False,
                "message": "Guardian not found",
                "error_code": "GUARDIAN_NOT_FOUND",
                "details": {"guardian_id": guardian_id},
            },
        )


class ChildNotFound(HTTPException):
    """Exception raised when child is not found"""
    
    def __init__(self, child_id: str) -> None:
        super().__init__(
            status_code=404,
            detail={
                "success": False,
                "message": "Child not found",
                "error_code": "CHILD_NOT_FOUND",
                "details": {"child_id": child_id},
            },
        )


class InvalidChildData(HTTPException):
    """Exception raised when child data is invalid"""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": message,
                "error_code": "INVALID_CHILD_DATA",
                "details": details,
            },
        )


class InvalidGuardianData(HTTPException):
    """Exception raised when guardian data is invalid"""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": message,
                "error_code": "INVALID_GUARDIAN_DATA",
                "details": details,
            },
        )


class GuardianNotActive(HTTPException):
    """Exception raised when guardian is not active"""
    
    def __init__(self, guardian_id: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Guardian is not active",
                "error_code": "GUARDIAN_NOT_ACTIVE",
                "details": {"guardian_id": guardian_id},
            },
        )


class TokenNotFound(HTTPException):
    """Exception raised when token is not found"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=404,
            detail={
                "success": False,
                "message": "Token not found",
                "error_code": "TOKEN_NOT_FOUND",
                "details": {"token_code": token_code},
            },
        )


class TokenAlreadyActive(HTTPException):
    """Exception raised when token is already active"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Token is already active",
                "error_code": "TOKEN_ALREADY_ACTIVE",
                "details": {"token_code": token_code},
            },
        )


class TokenAlreadyRevoked(HTTPException):
    """Exception raised when token is already revoked"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Token is already revoked",
                "error_code": "TOKEN_ALREADY_REVOKED",
                "details": {"token_code": token_code},
            },
        )


class TokenExpired(HTTPException):
    """Exception raised when token is expired"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Token is expired",
                "error_code": "TOKEN_EXPIRED",
                "details": {"token_code": token_code},
            },
        )


class ChildAlreadyHasActiveToken(HTTPException):
    """Exception raised when child already has an active token"""
    
    def __init__(self, child_id: str) -> None:
        super().__init__(
            status_code=409,
            detail={
                "success": False,
                "message": "Child already has an active token",
                "error_code": "CHILD_ALREADY_HAS_ACTIVE_TOKEN",
                "details": {"child_id": child_id},
            },
        )


class InvalidTokenFormat(HTTPException):
    """Exception raised when token format is invalid"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Invalid token format",
                "error_code": "INVALID_TOKEN_FORMAT",
                "details": {"token_code": token_code},
            },
        )


class TokenNotActiveForQR(HTTPException):
    """Exception raised when token is not active or issued for QR generation"""
    
    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Token is not active or issued for QR generation",
                "error_code": "TOKEN_NOT_ACTIVE_FOR_QR",
                "details": {"token_code": token_code},
            },
        )


class TokenNotActive(HTTPException):
    """Exception raised when token is not in ACTIVE status for scanner lookup"""

    def __init__(self, token_code: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": "Token is not active. Only active tokens can be scanned.",
                "error_code": "TOKEN_NOT_ACTIVE",
                "details": {"token_code": token_code},
            },
        )


class RescueSessionNotFound(HTTPException):
    """Exception raised when rescue session is not found"""

    def __init__(self, incident_id: str) -> None:
        super().__init__(
            status_code=404,
            detail={
                "success": False,
                "message": "Rescue session not found",
                "error_code": "RESCUE_SESSION_NOT_FOUND",
                "details": {"incident_id": incident_id},
            },
        )


class InvalidSessionStatusTransition(HTTPException):
    """Exception raised when an invalid status transition is attempted"""

    def __init__(self, current_status: str, requested_status: str) -> None:
        super().__init__(
            status_code=400,
            detail={
                "success": False,
                "message": f"Invalid status transition from {current_status} to {requested_status}",
                "error_code": "INVALID_SESSION_STATUS_TRANSITION",
                "details": {
                    "current_status": current_status,
                    "requested_status": requested_status,
                },
            },
        )


class ActiveRescueSessionExists(HTTPException):
    """Exception raised when child already has an active rescue session"""

    def __init__(self, child_id: str) -> None:
        super().__init__(
            status_code=409,
            detail={
                "success": False,
                "message": "Child already has an active rescue session",
                "error_code": "ACTIVE_RESCUE_SESSION_EXISTS",
                "details": {"child_id": child_id},
            },
        )


class QRGenerationFailed(HTTPException):
    """Exception raised when QR code generation fails"""
    
    def __init__(self, message: str = "Failed to generate QR code") -> None:
        super().__init__(
            status_code=500,
            detail={
                "success": False,
                "message": message,
                "error_code": "QR_GENERATION_FAILED",
                "details": None,
            },
        )


def register_exception_handlers(app) -> None:
    """Register global exception handlers for the FastAPI app"""
    
    @app.exception_handler(GuardianAlreadyExists)
    async def guardian_already_exists_handler(
        request: Request, exc: GuardianAlreadyExists
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(GuardianNotFound)
    async def guardian_not_found_handler(
        request: Request, exc: GuardianNotFound
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(ChildNotFound)
    async def child_not_found_handler(
        request: Request, exc: ChildNotFound
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(InvalidChildData)
    async def invalid_child_data_handler(
        request: Request, exc: InvalidChildData
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(InvalidGuardianData)
    async def invalid_guardian_data_handler(
        request: Request, exc: InvalidGuardianData
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(GuardianNotActive)
    async def guardian_not_active_handler(
        request: Request, exc: GuardianNotActive
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenNotFound)
    async def token_not_found_handler(
        request: Request, exc: TokenNotFound
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenAlreadyActive)
    async def token_already_active_handler(
        request: Request, exc: TokenAlreadyActive
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenAlreadyRevoked)
    async def token_already_revoked_handler(
        request: Request, exc: TokenAlreadyRevoked
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenExpired)
    async def token_expired_handler(
        request: Request, exc: TokenExpired
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(ChildAlreadyHasActiveToken)
    async def child_already_has_active_token_handler(
        request: Request, exc: ChildAlreadyHasActiveToken
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(InvalidTokenFormat)
    async def invalid_token_format_handler(
        request: Request, exc: InvalidTokenFormat
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenNotActiveForQR)
    async def token_not_active_for_qr_handler(
        request: Request, exc: TokenNotActiveForQR
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(TokenNotActive)
    async def token_not_active_handler(
        request: Request, exc: TokenNotActive
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(QRGenerationFailed)
    async def qr_generation_failed_handler(
        request: Request, exc: QRGenerationFailed
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(RescueSessionNotFound)
    async def rescue_session_not_found_handler(
        request: Request, exc: RescueSessionNotFound
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(InvalidSessionStatusTransition)
    async def invalid_session_status_transition_handler(
        request: Request, exc: InvalidSessionStatusTransition
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(ActiveRescueSessionExists)
    async def active_rescue_session_exists_handler(
        request: Request, exc: ActiveRescueSessionExists
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
