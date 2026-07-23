"""Request/Response Logging Middleware"""
import time
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            },
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            },
        )
        
        return response


def setup_logging(app: FastAPI) -> None:
    """Configure logging middleware for the application"""
    app.add_middleware(LoggingMiddleware)