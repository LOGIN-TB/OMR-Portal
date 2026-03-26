# OMR-Portal

Self-service portal for spamgo relay server customers. Provides SMTP account statistics, DNS status checks, password management, and automated warnings.

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose (for production)

### Development

1. Copy config files:

```bash
cp config/servers.json.example config/servers.json
cp .env.example .env
```

2. Edit `config/servers.json` with your relay server credentials.

3. Edit `.env` and set a strong `JWT_SECRET`.

4. Backend:

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
JWT_SECRET=dev-secret uvicorn app.main:app --reload
```

5. Frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to the backend at `localhost:8000`.

### Production (Docker)

```bash
docker compose up --build -d
```

The portal runs behind Caddy with automatic HTTPS on `my.spamgo.de`.

## Architecture

- **Backend:** FastAPI + SQLAlchemy (async) + SQLite
- **Frontend:** Vue 3 + TypeScript + PrimeVue + Pinia
- **Aggregator:** Queries N relay servers in parallel via `/api/portal/*` endpoints
- **Scheduler:** APScheduler for quota, DNS, RBL, and bounce rate checks
- **Auth:** Magic link login, JWT stored as HttpOnly cookie
