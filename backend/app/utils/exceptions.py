"""Custom Exception Handlers"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.logger import logger


class ChildDNAException(HTTPException):
    """Base exception for Child DNA application"""
    
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


async def child_dna_exception_handler(request: Request, exc: ChildDNAException):
    """Global exception handler for Child DNA exceptions"""
    logger.error(f"Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )