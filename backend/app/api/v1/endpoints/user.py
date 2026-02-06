import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_or_create_user
from app.api.v1.schemas import UserInfoOut
from app.models.event_log import EventLog

LOG = logging.getLogger("app.api.user")

router = APIRouter()

@router.get("/info", response_model=UserInfoOut)
def user_info(telegram_id: int, db: Session = Depends(get_db)):
    user = get_or_create_user(db, telegram_id)
    db.add(EventLog(event="user.info", data={"telegram_id": telegram_id}))
    db.commit()
    return UserInfoOut(id=user.id, telegram_id=user.telegram_id, role=user.role.value)
