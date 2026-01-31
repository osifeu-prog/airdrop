import logging
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.token_config import TokenConfig
from app.services.redis_client import init_redis

LOG = logging.getLogger("app.token")

PRICE_KEY = "token:price"
MAX_AIRDROP_KEY = "token:max_airdrop_per_user"

def get_config(db: Session) -> TokenConfig:
    cfg = db.query(TokenConfig).filter(TokenConfig.id == 1).first()
    if cfg is None:
        cfg = TokenConfig(id=1, price=Decimal("1"), max_airdrop_per_user=100)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg

def get_price(db: Session) -> Decimal:
    try:
        r = init_redis.client()
        v = r.get(PRICE_KEY)
        if v is not None:
            return Decimal(v)
    except Exception:
        pass

    cfg = get_config(db)
    try:
        init_redis.client().set(PRICE_KEY, str(cfg.price))
    except Exception:
        pass
    return cfg.price

def set_price(db: Session, price: Decimal) -> Decimal:
    cfg = get_config(db)
    cfg.price = price
    db.add(cfg)
    db.commit()
    try:
        init_redis.client().set(PRICE_KEY, str(price))
    except Exception:
        pass
    return price

def get_max_airdrop(db: Session) -> int:
    try:
        r = init_redis.client()
        v = r.get(MAX_AIRDROP_KEY)
        if v is not None:
            return int(v)
    except Exception:
        pass
    cfg = get_config(db)
    try:
        init_redis.client().set(MAX_AIRDROP_KEY, str(cfg.max_airdrop_per_user))
    except Exception:
        pass
    return int(cfg.max_airdrop_per_user)

def set_max_airdrop(db: Session, max_airdrop_per_user: int) -> int:
    cfg = get_config(db)
    cfg.max_airdrop_per_user = max_airdrop_per_user
    db.add(cfg)
    db.commit()
    try:
        init_redis.client().set(MAX_AIRDROP_KEY, str(max_airdrop_per_user))
    except Exception:
        pass
    return max_airdrop_per_user
