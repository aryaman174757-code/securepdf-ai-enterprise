import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "SecurePDF AI Enterprise"
    PROJECT_VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Security & Cryptography
    SECRET_KEY: str = Field(default="enterprise_super_secret_key_change_in_production_min_32_bytes_x98f", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_SCHEME: str = "argon2"

    # Zero-Trust Ephemeral Storage
    ZERO_TRUST_TEMP_DIR: str = Field(default="/tmp/securepdf_ephemeral", env="ZERO_TRUST_TEMP_DIR")
    AUTO_WIPE_AFTER_SECONDS: int = 1800  # 30 min default TTL
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/markdown",
        "text/html"
    ]

    # Database & Storage
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/securepdf_db", env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")

    # Qdrant Vector DB
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    QDRANT_COLLECTION_PREFIX: str = "securepdf_tenant_"

    # AI & LLM Services
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024
    RERANKER_MODEL: str = "BAAI/bge-reranker-large"
    DEFAULT_LLM_MODEL: str = "deepseek-chat"

    # CORS Whitelist
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://app.securepdf.ai"
    ]

    # Rate Limiting (Free vs Pro)
    FREE_RATE_LIMIT_PER_MIN: int = 5
    FREE_HEAVY_JOBS_PER_DAY: int = 3
    PRO_RATE_LIMIT_PER_MIN: int = 60
    PRO_HEAVY_JOBS_PER_DAY: int = 200

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
