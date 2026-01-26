# AGENTS.md — Internal Support & Status Portal (Azure Databricks Apps)

## Setup & commands (canonical)

Best practice: run commands from repo root unless stated otherwise.

### Local dev (recommended modes)

#### Mode A — fast inner loop (Vite + FastAPI separately)

Use this when actively building UI/API.

```bash
# Frontend dev server (hot reload)
cd frontend
npm ci
npm run dev

# Backend dev server (hot reload)
cd ../backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Notes:
- In Mode A, the backend must support a DEV identity override (see Auth section).
- Frontend should proxy `/api/*` to the backend.

#### Mode B — end-to-end "Databricks Apps-like" (injects forwarded headers)

Use this when validating auth + headers + serving the built SPA from FastAPI.

```bash
# Build frontend assets first (served by FastAPI static mounting)
cd frontend
npm ci
npm run build

# Run via Databricks Apps local proxy (injects app-specific headers)
cd ..
databricks apps run-local --prepare-environment --debug
# Open: http://localhost:8001
```

### Lint / format

```bash
# Backend
cd backend
ruff check .
ruff format .
mypy .

# Frontend
cd ../frontend
npm run lint
npm run format
```

### Tests

```bash
# Backend
cd backend
pytest -q

# Frontend
cd ../frontend
npm test

# Optional: full E2E (if present)
npm run test:e2e
```

### Build (CI)

```bash
# Frontend build
cd frontend
npm ci
npm run build

# Backend checks
cd ../backend
python -m compileall .
ruff check .
pytest -q
```

### Deploy (Databricks Asset Bundle)

```bash
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run portal_app -t dev
```

---

## Hard boundaries (do / don't)

### Always do

- Keep request handlers "read-only" from external systems: the portal reads Delta tables; scheduled jobs do external polling.
- Run lint + tests for the touched area before opening a PR.
- Preserve auditability: all write tables include `created_at/by`, `updated_at/by` and never lose history.
- Log request correlation using request id headers (and include user attribution where available).

### Ask first (or create an ADR) before

- Changing authentication strategy (e.g., enabling OBO / user-scoped reads).
- Changing table schemas or retention policies in a way that breaks queries.
- Introducing new external dependencies that require outbound internet at runtime.
- Adding attachments / file uploads (security implications).

### Never do

- Never commit secrets (tokens, client secrets, tenant ids if sensitive, etc.).
- Never store secrets in `app.yaml` as plaintext; only reference managed secrets/resources.
- Never add request-time calls to Power BI/Fabric/other APIs (keep status ingestion async).
- Never weaken RBAC checks "just for MVP" on write/state-change endpoints.

---

## Project goal (what we are building)

A single internal portal where platform users can:

- View platform health (Databricks + Power BI/Fabric) and data freshness.
- Submit incidents/bugs and improvement requests (with voting).
- Submit "my platform" service requests (access/onboarding/change).
- Read user documentation + business glossary.
- See roadmap and status messages.

Hosted as a Databricks App:

- FastAPI serves REST endpoints and the built React SPA (single origin).
- Delta-only backend tables (Unity Catalog) for now.
- Scheduled ingestion jobs write normalized status results into Delta.

---

## Repo layout (expected)

If the repo differs, update this section.

```
.
├── backend/                      # FastAPI service
│   ├── app/
│   │   ├── main.py               # FastAPI app + routers + static mounting
│   │   ├── api/v1/               # versioned REST endpoints
│   │   ├── auth/                 # header parsing, RBAC
│   │   ├── db/                   # query layer (Delta via SQL warehouse)
│   │   ├── models/               # pydantic schemas
│   │   └── services/             # domain logic (status, tickets, docs)
│   ├── tests/
│   └── requirements.txt
├── frontend/                     # React SPA (Vite)
│   ├── src/
│   ├── public/
│   └── package.json
├── jobs/                         # scheduled ingestion jobs (status)
│   ├── src/
│   └── notebooks/                # optional
├── infra/
│   ├── databricks.yml            # asset bundle
│   └── app.yaml                  # app command + env/resources
└── docs/                         # user-facing docs (markdown)
```

---

## Runtime facts (Databricks Apps)

When running inside Databricks Apps:

- App runs on Python 3.11 and Node 22.
- App should bind to `DATABRICKS_APP_PORT`.
- Service principal credentials are injected via environment variables (client id + secret).
- Reverse proxy forwards a known set of `X-Forwarded-*` headers (user attribution + request id).

Agents: do not hardcode ports or credentials.

---

## Authentication & identity (MVP rules)

### Sources of identity

- Service principal (app identity) is used for all data reads/writes.
- User attribution for writes:
  - prefer `X-Forwarded-User`
  - fallback to `X-Forwarded-Email`
  - also capture `X-Forwarded-Preferred-Username` if present

### Trust model

- In Databricks Apps: treat forwarded headers as provided by the platform reverse proxy.
- In local dev: headers may be missing; simulate them.

### MVP enforcement (recommended)

- Reads (status + docs): allowed with app identity, but still apply visibility rules.
- Writes (tickets/comments/votes/state changes): require user identity headers.
- If missing, return 401/403 (do not attribute to app service principal).

### DEV override (Mode A)

For local dev only, allow a `DEV_USER` / `DEV_EMAIL` env var override that:

- sets request user identity when forwarded headers are missing
- is disabled automatically when `DATABRICKS_HOST` / Apps env is detected

---

## API conventions

### Versioning

- All REST endpoints live under `/api/v1/...`.
- Backward compatible changes are allowed in v1.
- Breaking changes require `/api/v2` (do not silently break clients).

### Error shape

Standardize on:

```json
{
  "error": {
    "code": "string",
    "message": "human readable",
    "request_id": "uuid"
  }
}
```

### Pagination

Any list endpoint must support:

- `limit` (default 25, max 200)
- `cursor` or `offset`
- stable ordering (usually `created_at desc`)

### SPA routing

React routes must be handled by a FastAPI "catch-all" that serves `index.html` for unknown paths, while `/api/*` stays API-only.

---

## Serving the React SPA from FastAPI (single origin)

Default approach:

- Frontend builds to `frontend/dist/`.
- CI copies build output into `backend/app/static/` (or similar).
- FastAPI mounts static assets and serves SPA.

Example (pattern only; adjust paths):

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="app/static", html=True), name="spa")
```

If you change this strategy (e.g., host SPA separately), you must:

- define allowed origins (CORS)
- document the origin(s) in this file

---

## Delta-only data model rules

### Naming and identity

- All tables live under Unity Catalog: `<catalog>.<schema>.<table>`.
- Primary keys are UUID strings: `id`.
- Foreign keys are "logical" (enforced in code).

### Required columns (all core tables)

- `id` (uuid string)
- `platform_id` (string, nullable where appropriate)
- `state` (string)
- `created_at`, `created_by`
- `updated_at`, `updated_by`
- Optional: `is_deleted` (soft delete), `deleted_at/by`

Writes must be idempotent where possible:

- Use `MERGE` for upserts (votes, state transitions, platform defs).
- Prefer append-only for event/audit tables (`*_events`, `status_results`).

### Concurrency

For mutable work items:

- use version integer (optimistic concurrency)
- state change endpoint requires `expected_version`
- API returns 409 on conflict

---

## Status ingestion rules (no external calls at request time)

### Tables (minimum)

- `status_checks` (definitions + SLA thresholds)
- `status_results` (time series)
- `status_ingestion_runs` (job run metadata)
- `status_messages` (manual comms)

### Ingestion job contract

Each scheduled run:

1. insert `status_ingestion_runs` row (RUNNING)
2. write results to `status_results`
3. update run row to SUCCESS/FAIL (with error summary)

UI should compute:

- freshness vs SLA
- last successful update
- "unknown" when ingestion stale or failing

---

## RBAC (must exist before "admin" features)

Define roles early (minimum):

- Viewer
- Contributor (create items)
- IncidentTriager (change incident state, assign)
- ServiceOwner (publish status messages for owned platforms)
- Admin (platform definitions, RBAC bindings)

MVP approach:

- `role_bindings` Delta table or Entra snapshot table
- enforce RBAC in backend (never only in UI)

---

## Docs + glossary rules

Docs:

- Git-backed Markdown rendered in-app.
- Do not allow raw HTML unless explicitly sanitized/approved.
- If docs are pulled at runtime, ensure networking + auth are planned; otherwise prefer build-time bundling.

Glossary:

- Delta-backed: `term`, `definition`, `steward`, `status`, `related_assets`
- Include search endpoint with pagination.

---

## Logging & observability (MVP)

Backend must log (structured JSON preferred):

- request path + method
- response status
- latency
- `X-Request-Id` (or generated id)
- user identity (when present)
- `platform_id` and `item_id` for ticket actions

Expose:

- `/api/v1/healthz` (fast local check)
- `/api/v1/readyz` (can we query required tables/warehouse?)

---

## Decisions required (keep short; update as decisions are made)

1. SPA build & deploy
   - Build in CI and bundle into app package (default)
   - Serve separately (requires CORS + hosting)
2. API versioning
   - `/api/v1` prefix (default)
   - no version prefix (discouraged)
3. Identity fallback
   - deny writes when user headers missing (default)
   - allow writes as service principal (discouraged)
4. SLA thresholds
   - per-check in `status_checks` (default)
   - hardcoded in code (discouraged)
5. Global health rollup
   - max severity across platforms (simple)
   - weighted aggregation (needs config)
6. Retention
   - `status_results` retention (e.g., 90d) + rollups
   - ticket retention + archive policy
7. Power BI/Fabric
   - API approach + auth (service principal, scopes)
   - network policies/NCC readiness
