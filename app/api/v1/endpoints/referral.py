from fastapi import APIRouter
from backend.app.db.database import SessionLocal
from backend.app.models.user import User

router = APIRouter()

@router.get("/link")
def link(username: str):

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()

    return {
        "link": f"https://your-domain.com/r/{user.referral_code}"
    }
