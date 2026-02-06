from fastapi import APIRouter
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
import uuid

router = APIRouter()

@router.post("/register")
def register(username: str, invited_by: str | None = None):
    db = SessionLocal()

    referral_code = str(uuid.uuid4())[:8]

    user = User(
        username=username,
        referral_code=referral_code,
        invited_by=invited_by
    )

    db.add(user)

    if invited_by:
        inviter = db.query(User).filter(User.referral_code == invited_by).first()
        if inviter:
            inviter.balance += 50

    db.commit()
    db.refresh(user)

    return {
        "username": user.username,
        "referral": user.referral_code
    }
