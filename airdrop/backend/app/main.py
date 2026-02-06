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
