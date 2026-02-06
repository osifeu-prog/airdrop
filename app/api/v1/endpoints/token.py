import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, require_admin_secret
from app.api.v1.schemas import TokenPriceOut, TokenPriceSetIn
from app.models.event_log import EventLog
from app.services import token as token_svc

LOG = logging.getLogger("app.api.token")

router = APIRouter()

@router.get("/price", response_model=TokenPriceOut)
def get_price(db: Session = Depends(get_db)):
    price = token_svc.get_price(db)
    max_airdrop = token_svc.get_max_airdrop(db)
    db.add(EventLog(event="token.price.get", data={}))
    db.commit()
    return TokenPriceOut(price=price, max_airdrop_per_user=max_airdrop)

@router.post("/price", response_model=TokenPriceOut, dependencies=[Depends(require_admin_secret)])
def set_price(body: TokenPriceSetIn, db: Session = Depends(get_db)):
    if body.price is not None:
        token_svc.set_price(db, body.price)
    if body.max_airdrop_per_user is not None:
        token_svc.set_max_airdrop(db, body.max_airdrop_per_user)
    price = token_svc.get_price(db)
    max_airdrop = token_svc.get_max_airdrop(db)
    db.add(EventLog(event="token.price.set", data={"price": str(price), "max_airdrop_per_user": max_airdrop}))
    db.commit()
    return TokenPriceOut(price=price, max_airdrop_per_user=max_airdrop)
