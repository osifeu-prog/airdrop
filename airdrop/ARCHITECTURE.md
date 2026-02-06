# Architecture

## Components

### 1) Backend (FastAPI)
- API v1 under `backend/app/api/v1`
- SQLAlchemy ORM models under `backend/app/models`
- DB session provider under `backend/app/db/session.py`
- Redis client under `backend/app/services/redis_client.py`
- Cross-cutting concerns:
  - Request logging middleware (`backend/app/core/logging.py`)
  - Feature flags (`backend/app/services/feature_flags.py`)
  - Token config + Redis cache (`backend/app/services/token.py`)
  - Rate limiting (`backend/app/services/rate_limit.py`)
  - Queue abstraction (`backend/app/services/queue.py`)

### 2) Worker
`backend/app/worker.py`
- Blocking loop reading from Redis queue `queue:airdrop_auto_approve`
- Sleeps `AUTO_APPROVE_DELAY_SECONDS`
- Approves PENDING airdrops and credits user wallets
- Writes audit logs to `event_logs`

### 3) Telegram Bot
`bot/main.py`
- Long polling by default
- Minimal menu + airdrop request + balance
- Admin helper commands:
  - /admin_set_price
  - /admin_approve
  - /admin_reject

### 4) WebApp
`webapp/`
- Vanilla HTML/JS
- Uses Telegram WebApp context when inside Telegram
- Uses DEV fallback outside Telegram

The backend serves `webapp/` under `GET /webapp/*`.

---

## Data model (Postgres)

- `users`
  - `telegram_id` unique
  - `role`: user/admin/system
  - `created_at`, `last_seen`
- `wallets`
  - `user_id` PK/FK
  - `balance` numeric
- `airdrops`
  - `user_id` FK
  - `amount`, `status`, `created_at`
- `token_config`
  - singleton row `id=1`
  - `price`, `max_airdrop_per_user`
- `feature_flags`
  - toggles with caching to Redis
- `event_logs`
  - append-only-ish event data

---

## Security

- Admin endpoints require `X-Admin-Secret` (env `ADMIN_SECRET`)
- Telegram WebApp initData can be verified via HMAC using `TELEGRAM_BOT_TOKEN`
- In DEBUG mode, verification failures are tolerated to enable local dev

---

## Observability

- `backend/logging.conf` logs to console + `backend.log`
- request middleware logs method/path/status/latency and attaches `X-Request-Id`

---

## Versioning

- API is namespaced under `/api/v1`
- future v2 can be added under `backend/app/api/v2`
