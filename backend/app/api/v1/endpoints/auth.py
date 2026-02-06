<<<<<<< HEAD
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas import TelegramAuthIn, UserInfoOut
from app.api.v1.deps import get_db, get_or_create_user
from app.core.config import settings
from app.models.event_log import EventLog
from app.utils.security import verify_telegram_init_data

LOG = logging.getLogger("app.api.auth")

router = APIRouter()

@router.post("/telegram", response_model=UserInfoOut)
def auth_telegram(payload: TelegramAuthIn, db: Session = Depends(get_db)):
    ok = verify_telegram_init_data(payload.init_data, settings.TELEGRAM_BOT_TOKEN)
    if not ok and not settings.DEBUG:
        raise HTTPException(status_code=401, detail="Invalid initData signature")

    user = get_or_create_user(db, payload.telegram_id)

    db.add(EventLog(event="auth.telegram", data={"telegram_id": payload.telegram_id}))
    db.commit()

    return UserInfoOut(id=user.id, telegram_id=user.telegram_id, role=user.role.value)
=======
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
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
