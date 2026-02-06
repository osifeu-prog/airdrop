from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.wallet import Wallet

def require_admin_secret(x_admin_secret: str | None = Header(default=None, alias="X-Admin-Secret")) -> None:
    if not x_admin_secret or x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

def get_or_create_user(db: Session, telegram_id: int) -> User:
    u = db.query(User).filter(User.telegram_id == telegram_id).first()
    if u is None:
        u = User(telegram_id=telegram_id, role=UserRole.USER)
        db.add(u)
        db.commit()
        db.refresh(u)
        # create wallet
        w = Wallet(user_id=u.id)
        db.add(w)
        db.commit()
    return u
