import json
import logging
from app.services.redis_client import init_redis

LOG = logging.getLogger("app.queue")

QUEUE_KEY = "queue:airdrop_auto_approve"

def enqueue_airdrop(airdrop_id: int) -> None:
    try:
        init_redis.client().rpush(QUEUE_KEY, json.dumps({"airdrop_id": airdrop_id}))
    except Exception:
        # Fail-open: if Redis is down, auto-approve won't run, but request still succeeds.
        LOG.warning("Redis unavailable; cannot enqueue airdrop %s for auto-approve.", airdrop_id, exc_info=True)

def pop_airdrop(timeout: int = 5):
    try:
        res = init_redis.client().brpop(QUEUE_KEY, timeout=timeout)
        if not res:
            return None
        _, payload = res
        return json.loads(payload)
    except Exception:
        LOG.warning("Redis unavailable; worker queue idle.", exc_info=True)
        return None
