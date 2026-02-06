import base64
import hashlib
import hmac
import logging
from urllib.parse import parse_qsl

from app.core.config import settings

LOG = logging.getLogger("app.security")

def verify_telegram_init_data(init_data: str, bot_token: str) -> bool:
    '''
    Verify Telegram WebApp initData (HMAC-SHA256).
    Telegram docs: data-check-string + secret_key=sha256(bot_token)
    '''
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
        if "hash" not in pairs:
            return False
        received_hash = pairs.pop("hash")

        data_check_string = "\n".join([f"{k}={pairs[k]}" for k in sorted(pairs.keys())])

        secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        return hmac.compare_digest(computed_hash, received_hash)
    except Exception:
        LOG.exception("Failed to verify initData.")
        return False
