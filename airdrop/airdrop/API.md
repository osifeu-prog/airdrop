# API v1

Base prefix: `/api/v1`

## Auth
### `POST /api/v1/auth/telegram`
Verifies Telegram WebApp `initData` (in production). In DEBUG mode, signature failures are tolerated.

Body:
```json
{
  "telegram_id": 123,
  "init_data": "query_id=...&user=...&hash=..."
}
```

Response:
```json
{ "id": 1, "telegram_id": 123, "role": "user" }
```

## User
### `GET /api/v1/user/info?telegram_id=123`
Creates or fetches user + wallet.

## Wallet
### `GET /api/v1/wallet/balance?telegram_id=123`
Returns wallet balance.

## Airdrop
### `POST /api/v1/airdrop/request?telegram_id=123`
Rate-limited via Redis. Creates a PENDING airdrop and (optionally) enqueues auto-approval.

Body:
```json
{ "amount": "10" }
```

### `POST /api/v1/airdrop/approve`
Admin-only. Header `X-Admin-Secret: <ADMIN_SECRET>`

Body:
```json
{ "airdrop_id": 1 }
```

### `POST /api/v1/airdrop/reject`
Admin-only.

## Token
### `GET /api/v1/token/price`
Returns token price + max airdrop per user (cached in Redis).

### `POST /api/v1/token/price`
Admin-only. Allows updating `price` and/or `max_airdrop_per_user`.

## Admin (Feature Flags)
### `POST /api/v1/admin/feature-flag`
Admin-only.

Body:
```json
{ "key": "AUTO_APPROVE_ENABLED", "enabled": true }
```
