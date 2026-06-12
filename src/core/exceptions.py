"""
Global exception handlers for consistent error responses across the API.
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception with a structured response."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException):
    """
    Global handler for AppException subclasses.
    Returns a consistent JSON error payload.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "detail": exc.message},
    )
