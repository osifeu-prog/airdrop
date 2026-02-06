<<<<<<< HEAD
﻿from app.routes.health import router as health_router
import time
import logging
import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.db.session import init_db
from app.redis.client import init_redis

LOG = logging.getLogger("app")

def create_app() -> FastAPI:
    app = FastAPI(title="Airdrop Platform", version="stable")

    @app.on_event("startup")
    def _startup():
        # ---- DB (safe) ----
        try:
            if settings.DATABASE_URL and os.getenv("DB_DISABLED") != "1":
                if callable(init_db):
                    init_db()
                elif hasattr(init_db, "configure"):
                    init_db.configure(settings.DATABASE_URL)

            if hasattr(init_db, "is_enabled") and init_db.is_enabled():
                LOG.info("DB enabled.")
            else:
                LOG.warning("DB disabled (local).")
        except Exception as e:
            LOG.exception("DB init failed (ignored): %s", e)

        # ---- Redis (safe) ----
        try:
            if settings.REDIS_URL and os.getenv("REDIS_DISABLED") != "1":
                if callable(init_redis):
                    init_redis()
                elif hasattr(init_redis, "configure"):
                    init_redis.configure(settings.REDIS_URL)
        except Exception as e:
            LOG.exception("Redis init failed (ignored): %s", e)

        # ---- Bootstrap (LOCAL ONLY) ----
        try:
            if settings.ENVIRONMENT.lower() == "local" and hasattr(init_db, "is_enabled") and init_db.is_enabled():
                init_db.ensure_bootstrap()
                LOG.info("DB bootstrap ensured (local).")
            else:
                LOG.warning("DB bootstrap skipped.")
        except Exception as e:
            LOG.exception("DB bootstrap failed (ignored): %s", e)

        LOG.info("Startup complete.")

    @app.on_event("shutdown")
    def _shutdown():
        try:
            init_redis.close()
        except Exception:
            pass
        try:
            init_db.close()
        except Exception:
            pass
        LOG.info("Shutdown complete.")

    

    @app.get("/public/progress", include_in_schema=False)
    def _public_progress_legacy_redirect():
        return RedirectResponse(
            url="/api/v1/public/progress",
            status_code=307,
        )

    return app


app = create_app()
app.include_router(health_router)



=======
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import engine, get_db
from backend.app.models import models
from backend.app.utils.cert_generator import generate_certificate
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# נתיב מוחלט לתיקיית התעודות בתוך ה-Container
CERT_DIR = os.path.join(os.getcwd(), "webapp", "certificates")
os.makedirs(CERT_DIR, exist_ok=True)

class UserIn(BaseModel):
    telegram_id: str
    username: str
    referrer_id: str = None

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/api/v2/register")
async def register(user: UserIn, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.telegram_id == user.telegram_id).first()
    if not db_user:
        db_user = models.User(telegram_id=user.telegram_id, username=user.username, referrer_id=user.referrer_id)
        db.add(db_user)
        db.commit()
    
    # יצירת התעודה
    generate_certificate(user.username, user.telegram_id)
    return {"status": "registered", "telegram_id": user.telegram_id}

app.mount("/certificates", StaticFiles(directory=CERT_DIR), name="certs")
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
