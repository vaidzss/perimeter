import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models  # Ensures all models are registered

# Create SQLite tables if they do not exist
Base.metadata.create_all(bind=engine)

# Ensure logs directory exists
os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Fictional UPI Neobank API - Target testbed for CC6-IC07 API Discovery & Abuse Prevention",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.middleware.structured_logger import StructuredLoggingMiddleware
app.add_middleware(StructuredLoggingMiddleware)

from app.api.v2.auth import router as auth_router
from app.api.v2.accounts import router as accounts_router
from app.api.v2.merchants import router as merchants_router
from app.api.v2.payments import router as payments_router

app.include_router(auth_router, prefix="/api/v2")
app.include_router(accounts_router, prefix="/api/v2")
app.include_router(merchants_router, prefix="/api/v2")
app.include_router(payments_router, prefix="/api/v2")

from app.api.v2.endpoints.provisioning import router as provisioning_router
from app.api.v2.endpoints.internal_reports import router as internal_reports_router
app.include_router(provisioning_router, prefix="/api/v2/internal")
app.include_router(internal_reports_router, prefix="/api/v2/internal")

# Deliberately vulnerable Shadow & Zombie routes (excluded from schema)
from app.api.v1.legacy_routes import router as legacy_router
from app.api.internal.debug_routes import router as debug_router

app.include_router(legacy_router, prefix="/api/v1", include_in_schema=False)
app.include_router(debug_router, prefix="/api/internal", include_in_schema=False)

from app.api.internal.reset_routes import router as reset_router
app.include_router(reset_router, prefix="/api", include_in_schema=False)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "bharatpay-backend",
        "version": "2.0.0",
        "watermark": settings.DATA_WATERMARK
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to BharatPay API",
        "environment": settings.ENV_NAME,
        "watermark": settings.DATA_WATERMARK
    }
