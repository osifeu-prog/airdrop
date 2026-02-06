# Airdrop Platform (Telegram Bot + WebApp + FastAPI + Postgres + Redis)

This repository is a complete, modular starter for an **internal/off‑chain airdrop system** with:
- FastAPI backend (API v1, feature flags, Redis cache/rate limit/queues)
- PostgreSQL (SQLAlchemy + Alembic)
- Redis (cache + rate limiting + simple queue)
- Telegram Bot (python-telegram-bot)
- Telegram WebApp (vanilla HTML/JS) served by the backend

> Security note: do **NOT** commit real tokens/secrets. Use `.env` locally and `.env.example` as reference.

---

## Folder structure

```
backend/
  app/
    api/v1/
    services/
    models/
    db/
    core/
    utils/
    tests/
  logging.conf
  main.py

bot/
  handlers/
  config.py
  main.py

webapp/
  index.html
  js/
  css/

infra/
  railway.json
  docker-compose.yml
  Dockerfile

migrations/
.env.example
README.md
ROADMAP.md
API.md
ARCHITECTURE.md
```

---

## Local development (Windows PowerShell)

### 0) Prereqs
- Python 3.11+
- Docker Desktop (recommended for Postgres + Redis)

### 1) Start Postgres + Redis
```powershell
docker compose -f .\infra\docker-compose.yml up -d
```

### 2) Create `.env`
Copy `.env.example` to `.env` and edit:
- `DATABASE_URL`
- `REDIS_URL`
- `ADMIN_SECRET`
- `TELEGRAM_BOT_TOKEN` (for bot + initData verification)

### 3) Setup
```powershell
.\setup.ps1
```

### 4) Run migrations
```powershell
.\migrate.ps1
```

### 5) Run (backend + worker + bot)
```powershell
.\run.ps1
```

Backend:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/webapp/index.html

---

## Smoke / unit tests

Unit tests (no external services required):
```powershell
.\test.ps1
```

If you want real smoke tests (DB/Redis), start docker compose first and hit:
- `GET /ready` (checks DB + Redis connectivity)

---

## Git hygiene (UTF-8 no BOM, LF)

Install repo hooks:
```powershell
.\tools\install-hooks.ps1
```

This activates `.githooks/pre-commit` to block:
- UTF‑8 BOM (U+FEFF)
- merge-conflict markers

---

## Railway deployment (recommended)

Create **3 services** in one Railway project (same repo, different start commands):
1) **backend**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
2) **worker**: `python -m backend.app.worker`
3) **bot**: `python -m bot.main`

Set variables in each service:
- `DATABASE_URL`
- `REDIS_URL`
- `ADMIN_SECRET`
- `TELEGRAM_BOT_TOKEN`

(Optionally use `infra/railway.json` as a reference.)

---

## Next steps

See:
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `API.md`
