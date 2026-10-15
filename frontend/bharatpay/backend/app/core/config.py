import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_CORE_DIR)
_BACKEND_DIR = os.path.dirname(_APP_DIR)
BHARATPAY_ROOT = os.path.dirname(_BACKEND_DIR)

DEFAULT_DB_PATH = os.path.join(BHARATPAY_ROOT, "bharatpay.db").replace("\\", "/")
DEFAULT_LOG_PATH = os.path.join(BHARATPAY_ROOT, "logs", "bharatpay_requests.jsonl").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "BharatPay Neobank"
    API_V2_STR: str = "/api/v2"
    SECRET_KEY: str = os.getenv("JWT_SECRET", "synthetic_demo_jwt_secret_cc6_ic07_bharatpay")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", DEFAULT_LOG_PATH)
    
    # Environment flag
    ENV_NAME: str = "synthetic-demo"
    DATA_WATERMARK: str = "SYNTHETIC TEST DATA — CC6-IC07"

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
