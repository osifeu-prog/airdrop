from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Airdrop Platform"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8080
    CORS_ORIGINS: str = "http://127.0.0.1:8000,http://localhost:8000"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/airdropdb"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    ADMIN_SECRET: str = "change-me"

    TELEGRAM_BOT_TOKEN: str = "123456:replace_me"
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = "change-me-webhook-secret"

    FEATURE_FLAGS: str = "AIRDROP_ENABLED,AUTO_APPROVE_ENABLED,WEBAPP_ENABLED"

    MAX_AIRDROP_PER_USER: int = 100
    RATE_LIMIT_PER_HOUR: int = 3
    DISABLE_RATE_LIMIT: bool = False
    AUTO_APPROVE_DELAY_SECONDS: int = 10

    WEBAPP_PUBLIC_PATH: str = "/webapp"

    @field_validator("BACKEND_PORT", mode="before")
    @classmethod
    def _coerce_backend_port(cls, v):
        # Railway / env may provide empty string -> treat as default
        if v is None:
            return 8080
        if isinstance(v, str) and v.strip() == "":
            return 8080
        return v

settings = Settings()
