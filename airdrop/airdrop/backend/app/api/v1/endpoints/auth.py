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
