"""
Titos API — Modular Middleware API

Entry point for the FastAPI application. Registers all module routers
and global exception handlers.

Usage:
    uvicorn src.main:app --reload
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.exceptions import AppException, app_exception_handler
from src.modules.example.router import router as example_router
from src.modules.lhc2otobo.router import router as lhc2otobo_router
from src.modules.timecondition.router import router as timecondition_router

# Application metadata from environment configuration.
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Modular middleware API for integrating external systems.",
)

# Register global exception handlers.
app.add_exception_handler(AppException, app_exception_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions.
    Returns a 500 Internal Server Error with the exception message.
    """
    return JSONResponse(
        status_code=500,
        content={"error": True, "detail": f"Internal server error: {exc}"},
    )


@app.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint.
    Returns the API status and version.

    Use this endpoint to verify the service is running
    (e.g., in Docker health checks or monitoring tools).
    """
    return {"status": "ok", "version": settings.app_version}


# ---- Register module routers ----
# Each module exposes its own APIRouter. Add new modules here:
# app.include_router(my_new_module.router)

app.include_router(example_router)
app.include_router(lhc2otobo_router)
app.include_router(timecondition_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
