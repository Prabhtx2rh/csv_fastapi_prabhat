import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.routes.students import router as student_router
from app.services.student_service import student_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the CSV once on startup; nothing to clean up on shutdown."""
    try:
        student_service.load()
    except FileNotFoundError as exc:
        logger.error(str(exc))
        raise SystemExit(1)
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# Global exception handlers
# ------------------------------------------------------------------

@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    logger.error(f"RuntimeError: {exc}")
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(student_router)


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    """Basic liveness probe."""
    return {"status": "ok", "service": APP_TITLE, "version": APP_VERSION}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to the {APP_TITLE}",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
