import logging
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.feature_flag import FeatureFlag
from app.services.redis_client import init_redis

LOG = logging.getLogger("app.flags")

REDIS_PREFIX = "ff:"

def _defaults():
    return {k.strip(): True for k in settings.FEATURE_FLAGS.split(",") if k.strip()}

def is_enabled(db: Session, key: str) -> bool:
    key = key.strip()
    defaults = _defaults()
    try:
        r = init_redis.client()
        val = r.get(f"{REDIS_PREFIX}{key}")
        if val is not None:
            return val == "1"
    except Exception:
        pass

    row = db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
    if row is None:
        return defaults.get(key, False)
    return bool(row.enabled)

def set_flag(db: Session, key: str, enabled: bool) -> None:
    key = key.strip()
    row = db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
    if row is None:
        row = FeatureFlag(key=key, enabled=enabled)
        db.add(row)
    else:
        row.enabled = enabled
    db.commit()

    try:
        r = init_redis.client()
        r.set(f"{REDIS_PREFIX}{key}", "1" if enabled else "0")
    except Exception:
        LOG.warning("Redis unavailable to cache flag.")
