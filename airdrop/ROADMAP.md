# Roadmap

## Stage 1 — MVP (off-chain internal airdrop) ✅
- Users + wallets + roles
- Token config + cached price in Redis
- Feature flags
- Airdrop request + approve/reject
- Rate limit via Redis
- Redis queue + worker auto-approval
- Bot commands /start /menu /airdrop /balance
- WebApp basic UI
- Alembic migration + scripts
- Logging + unit tests

## Stage 2 — UI upgrade
- Better WebApp (tables/history, admin view)
- Wallet & airdrop history screens
- Better Telegram message UI (Markdown-safe formatting)
- Telegram deep links for actions

## Stage 3 — TON on-chain integration
- On-chain wallet linking
- Deposit detection and reconciliation
- Optional withdrawal flow (policy-driven)

## Stage 4 — Advanced security
- Proper Telegram initData required everywhere
- JWT session tokens for WebApp
- Admin RBAC (DB roles, per-endpoint permissions)
- Audit log immutability (append-only / WORM strategy)

## Stage 5 — CI/CD
- GitHub Actions: tests + lint + migration checks
- Railway deploy gating

## Stage 6 — Scaling
- Move worker to dedicated queue system (RQ/ARQ/Celery)
- Horizontal scaling, Redis cluster
- DB indexing & partitioning for logs

## Stage 7 — Economy (NFT / tasks / missions)
- Task engine (quests)
- NFT badges / access tiers
- Referral system + rewards
