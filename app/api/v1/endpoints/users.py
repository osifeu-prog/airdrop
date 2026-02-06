from fastapi import APIRouter
from backend.app.db.database import SessionLocal
from backend.app.models.user import User

router = APIRouter()

@router.get("/me")
def me(username: str):

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    return {
        "balance": user.balance,
        "referral": user.referral_code
    }
