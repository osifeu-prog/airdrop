import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_or_create_user
from app.api.v1.schemas import WalletBalanceOut
from app.models.event_log import EventLog
from app.models.wallet import Wallet

LOG = logging.getLogger("app.api.wallet")

router = APIRouter()

@router.get("/balance", response_model=WalletBalanceOut)
def wallet_balance(telegram_id: int, db: Session = Depends(get_db)):
    user = get_or_create_user(db, telegram_id)
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    db.add(EventLog(event="wallet.balance", data={"telegram_id": telegram_id}))
    db.commit()
    return WalletBalanceOut(balance=wallet.balance)
