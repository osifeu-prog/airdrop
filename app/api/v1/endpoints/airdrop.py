<<<<<<< HEAD
﻿import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_or_create_user, require_admin_secret
from app.api.v1.schemas import AirdropRequestIn, AirdropOut, AirdropApproveIn
from app.models.airdrop import Airdrop, AirdropStatus
from app.models.event_log import EventLog
from app.models.wallet import Wallet
from app.services.rate_limit import allow
from app.services.token import get_max_airdrop
from app.services.feature_flags import is_enabled
from app.services.queue import enqueue_airdrop
from app.core.config import settings

LOG = logging.getLogger("app.api.airdrop")

router = APIRouter()

@router.post("/request", response_model=AirdropOut)
def request_airdrop(telegram_id: int, body: AirdropRequestIn, db: Session = Depends(get_db)):
    if not is_enabled(db, "AIRDROP_ENABLED"):
        raise HTTPException(status_code=403, detail="Airdrop disabled")

    # rate limit (can be disabled in local/dev)
    disable_rl = bool(getattr(settings, "DISABLE_RATE_LIMIT", False))
    if (not disable_rl) and settings.RATE_LIMIT_PER_HOUR > 0:
        rl_key = f"airdrop:{telegram_id}"
        if not allow(rl_key, settings.RATE_LIMIT_PER_HOUR, 3600):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    user = get_or_create_user(db, telegram_id)
    max_airdrop = get_max_airdrop(db)

    amount = body.amount
    if amount > Decimal(str(max_airdrop)):
        amount = Decimal(str(max_airdrop))

    a = Airdrop(user_id=user.id, amount=amount, status=AirdropStatus.PENDING)
    db.add(a)
    db.add(EventLog(event="airdrop.request", data={"telegram_id": telegram_id, "amount": str(amount)}))
    db.commit()
    db.refresh(a)

    if is_enabled(db, "AUTO_APPROVE_ENABLED"):
        enqueue_airdrop(a.id)

    return AirdropOut(id=a.id, user_id=a.user_id, amount=a.amount, status=a.status.value.upper())

@router.post("/approve", response_model=AirdropOut, dependencies=[Depends(require_admin_secret)])
def approve_airdrop(body: AirdropApproveIn, db: Session = Depends(get_db)):
    a = db.query(Airdrop).filter(Airdrop.id == body.airdrop_id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Airdrop not found")
    if a.status != AirdropStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Already {a.status.value}")

    a.status = AirdropStatus.APPROVED
    db.add(a)

    wallet = db.query(Wallet).filter(Wallet.user_id == a.user_id).first()
    wallet.balance = wallet.balance + a.amount
    db.add(wallet)

    db.add(EventLog(event="airdrop.approve", data={"airdrop_id": a.id, "amount": str(a.amount)}))
    db.commit()
    return AirdropOut(id=a.id, user_id=a.user_id, amount=a.amount, status=a.status.value.upper())

@router.post("/reject", response_model=AirdropOut, dependencies=[Depends(require_admin_secret)])
def reject_airdrop(body: AirdropApproveIn, db: Session = Depends(get_db)):
    a = db.query(Airdrop).filter(Airdrop.id == body.airdrop_id).first()
    if a is None:
        raise HTTPException(status_code=404, detail="Airdrop not found")
    if a.status != AirdropStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Already {a.status.value}")

    a.status = AirdropStatus.REJECTED
    db.add(a)
    db.add(EventLog(event="airdrop.reject", data={"airdrop_id": a.id}))
    db.commit()
    return AirdropOut(id=a.id, user_id=a.user_id, amount=a.amount, status=a.status.value.upper())



=======
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
>>>>>>> 03e5c1437b28768ba89ff31f6cea0fc62306fdf0
