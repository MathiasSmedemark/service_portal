# Local Development

This doc covers Mode A (Vite + FastAPI separately) for a fast inner loop.

## Mode A (recommended)

Run from repo root.

Frontend (hot reload):

```bash
cd frontend
npm ci
npm run dev
```

Backend (hot reload):

```bash
cd ../backend
uv venv
uv sync --dev
uv run uvicorn app.main:app --reload --port 8000 --env-file .env
```

Notes:
- The Vite dev server proxies `/api/*` to `http://localhost:8000` (see `frontend/vite.config.js`).
- The backend uses `DATABRICKS_APP_PORT` only when running `python -m app.main`; the `uvicorn` command above sets the port directly.

## Local identity override (DEV_USER / DEV_EMAIL)

Writes require user identity. In local Mode A, you can simulate identity by setting `DEV_USER` and/or `DEV_EMAIL`.
This override is ignored automatically when `DATABRICKS_HOST` or `DATABRICKS_APP_PORT` is set (i.e., Apps mode).

Setup:

```bash
cp backend/.env.example backend/.env
```

Then edit `backend/.env` with your local values (do not commit it).
