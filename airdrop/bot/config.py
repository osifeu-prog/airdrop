import os
from dotenv import load_dotenv

# Force load from project root .env and OVERRIDE existing environment values
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=True)

def _must(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

class Settings:
    TELEGRAM_BOT_TOKEN: str = _must("TELEGRAM_BOT_TOKEN")
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "change-me-super-secret")

    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

settings = Settings()