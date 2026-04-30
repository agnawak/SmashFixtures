# Fixture Generator

FastAPI + React app for generating balanced volleyball fixtures from tier-list Excel sheets.

## Cleaned Project Structure

```
.
├── backend/
│   ├── main.py         # FastAPI routes + startup wiring
│   ├── database.py     # SQLAlchemy engine/session/base
│   ├── models.py       # DB models (users)
│   ├── schemas.py      # Request/response schemas
│   ├── security.py     # Password hashing + API key generation
│   └── config.py       # Environment configuration
├── app.py              # Compatibility shim: imports backend.main:app
├── fixture.py          # Fixture generation engine
├── frontend/           # React + Vite frontend
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Features

- Fixture generation (`/generate`)
- Custom fixture generation (`/generate-custom`)
- Postgres-backed auth:
  - `POST /signup`
  - `POST /login`
- API key protected fixture endpoints via `X-API-Key`

## Environment Variables

Copy `.env.example` to `.env` and adjust values.

Required for Docker setup:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `ALLOWED_ORIGINS`

Optional:

- `APP_USERNAME` and `APP_PASSWORD` to auto-bootstrap an initial user on startup
- `API_KEY` for temporary backward-compatible static key support

## Run With Docker

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: internal service `db:5432`

## Local Run (Without Docker)

Backend:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8001
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

If backend runs on port `8001`, set:

```bash
VITE_API_URL=http://localhost:8001
```

## Cloudflare Tunnel

You can still add Cloudflare Tunnel via the `tunnel` service in `docker-compose.yml` by setting `TUNNEL_TOKEN`.
