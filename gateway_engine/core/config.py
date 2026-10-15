"""
SentinelAPI Gateway Configuration Settings.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    TARGET_SERVICE_URL: str = os.getenv("TARGET_SERVICE_URL", "http://127.0.0.1:8001")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sentinel.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    JWT_SECRET: str = os.getenv("TARGET_JWT_SECRET", "sentinel-fintech-jwt-secret-key-9841")
    JWT_ALGORITHM: str = "HS256"
    
    OPENAPI_SPEC_PATH: str = os.getenv(
        "OPENAPI_SPEC_PATH", 
        os.path.join(os.path.dirname(__file__), "..", "..", "target_service", "openapi_official.json")
    )
    
    TELEMETRY_QUEUE_MAX_SIZE: int = 10000
    SLIDING_WINDOW_SEC: int = 60
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
