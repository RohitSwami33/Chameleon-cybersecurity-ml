from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # ============================================================
    # PostgreSQL Database Configuration (NEW)
    # ============================================================
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "chameleon")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "chameleon123")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chameleon_db")
    
    # Algorithm A: HMAC-SHA256 session key
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "chameleon-default-session-secret-change-me")
    
    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        """Async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Sync PostgreSQL connection URL (for Alembic migrations)."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # ============================================================
    # Legacy MongoDB Configuration (kept for migration reference)
    # ============================================================
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = "chameleon_db"
    
    # ============================================================
    # Application Configuration
    # ============================================================
    GEOIP_API_URL: str = "http://ip-api.com/json/"
    TARPIT_THRESHOLD: int = 5
    TARPIT_DELAY_MIN: float = 2.0
    TARPIT_DELAY_MAX: float = 10.0
    CONFIDENCE_THRESHOLD: float = 0.7
    MAX_INPUT_LENGTH: int = 200
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-2024")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PORT: int = int(os.getenv("PORT", 8000))
    
    # ============================================================
    # LLM API Configuration
    # ============================================================
    # DeepSeek API (primary deception engine - OpenAI compatible)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "sk-b6c071d6ac964525b99e5114623526cd")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # GLM-5 API (alternative deception engine)
    GLM5_API_KEY: str = os.getenv("GLM5_API_KEY", "")
    GLM5_API_URL: str = os.getenv("GLM5_API_URL", "https://open.bigmodel.cn/api/paas/v3/model-api/chatglm_turbo/invoke")
    GLM5_MODEL: str = os.getenv("GLM5_MODEL", "chatglm_turbo")
    
    # LLM Provider selection: "deepseek" or "glm5"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deepseek")
    
    # Gemini API (fallback/alternative)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # LLM behavior settings
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "100"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    
    # ============================================================
    # Feature Flags
    # ============================================================
    USE_LLM_DECEPTION: bool = os.getenv("USE_LLM_DECEPTION", "true").lower() == "true"
    USE_MERKLE_INTEGRITY: bool = os.getenv("USE_MERKLE_INTEGRITY", "true").lower() == "true"
    FALLBACK_TO_STATIC_DECEPTION: bool = True

    # ============================================================
    # Blockchain (Sepolia) & Honeytoken Configuration
    # ============================================================
    SEPOLIA_RPC_URL: str = os.getenv("SEPOLIA_RPC_URL", "")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    HONEYPOT_DOMAIN: str = os.getenv("HONEYPOT_DOMAIN", "localhost:8000")

    # ============================================================
    # Webhooks for Alerting
    # ============================================================
    DISCORD_WEBHOOK_URL: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Hardcoded constants (not configurable via .env)
MODEL_PATH = "chameleon_char_cnn_gru.keras"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "chameleon2024"

# Default tenant settings for single-tenant mode
DEFAULT_TENANT_EMAIL = "admin@chameleon.local"
DEFAULT_TENANT_CREDITS = 10000

settings = Settings()
