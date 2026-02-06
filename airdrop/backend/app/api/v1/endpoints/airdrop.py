from fastapi import APIRouter
from backend.app.db.database import SessionLocal
from backend.app.models.user import User

router = APIRouter()

@router.post("/claim")
def claim(username: str):

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    if user.claimed:
        return {"claimed": False}

    user.balance += 100
    user.claimed = 1

    db.commit()

    return {"claimed": True, "balance": user.balance}
