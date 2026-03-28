import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.core.database import engine, Base

import app.models.db_models

from app.routes.students    import router as csv_router
from app.routes.db_students import router as db_router
from app.services.student_service import student_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        student_service.load()
    except FileNotFoundError as exc:
        logger.error(str(exc))
        raise SystemExit(1)
    yield


app = FastAPI(
    title       = APP_TITLE,
    description = APP_DESCRIPTION,
    version     = APP_VERSION,
    lifespan    = lifespan,
)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@app.exception_handler(Exception)
async def generic_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(csv_router)
app.include_router(db_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": APP_TITLE, "version": APP_VERSION}

@app.get("/", tags=["Health"])
def root():
    return {
        "message" : f"Welcome to {APP_TITLE}",
        "docs"    : "/docs",
        "endpoints": {
            "csv_data"   : "/data",
            "db_insert"  : "POST /db/insert",
            "db_students": "/db/students",
            "check_db"   : "/check_db",
        }
    }