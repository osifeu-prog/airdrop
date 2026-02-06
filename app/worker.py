import logging
import time
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import init_db
from app.services.redis_client import init_redis
from app.services.queue import pop_airdrop
from app.models.airdrop import Airdrop, AirdropStatus
from app.models.wallet import Wallet
from app.models.event_log import EventLog
from app.services.feature_flags import is_enabled

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))
LOG = logging.getLogger("app.worker")

def approve(db: Session, airdrop_id: int) -> None:
    a = db.query(Airdrop).filter(Airdrop.id == airdrop_id).first()
    if a is None or a.status != AirdropStatus.PENDING:
        return
    a.status = AirdropStatus.APPROVED
    wallet = db.query(Wallet).filter(Wallet.user_id == a.user_id).first()
    wallet.balance = wallet.balance + a.amount
    db.add(wallet)
    db.add(a)
    db.add(EventLog(event="airdrop.auto_approve", data={"airdrop_id": a.id, "amount": str(a.amount)}))
    db.commit()

def main():
    init_db.configure(settings.DATABASE_URL)
    init_redis.configure(settings.REDIS_URL)

    LOG.info("Worker started. Waiting for jobs...")
    while True:
        job = pop_airdrop(timeout=5)
        if job is None:
            continue
        airdrop_id = int(job["airdrop_id"])
        try:
            with init_db.session() as db:
                if not is_enabled(db, "AUTO_APPROVE_ENABLED"):
                    LOG.info("AUTO_APPROVE disabled. Skipping.")
                    continue
                time.sleep(settings.AUTO_APPROVE_DELAY_SECONDS)
                approve(db, airdrop_id)
                LOG.info("Approved airdrop_id=%s", airdrop_id)
        except Exception:
            LOG.exception("Failed processing job: %s", job)

if __name__ == "__main__":
    main()
