from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "chameleon_db"
    GEOIP_API_URL: str = "http://ip-api.com/json/"
    TARPIT_THRESHOLD: int = 5
    TARPIT_DELAY_MIN: float = 2.0
    TARPIT_DELAY_MAX: float = 10.0
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_INPUT_LENGTH: int = 200
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

# Hardcoded constants (not configurable via .env)
MODEL_PATH = "chameleon_char_cnn_gru.keras"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "chameleon2024"

settings = Settings()
