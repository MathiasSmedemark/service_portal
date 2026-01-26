# Internal Support & Status Portal on Azure Databricks Apps

You're building a service portal for a Databricks data platform that combines platform health + data freshness, support intake, and self-service documentation — all hosted as an Azure Databricks App with a FastAPI backend and React SPA frontend, backed by Delta tables only (for now).

This is a solid direction because Databricks Apps gives you:

- A managed runtime for web apps (Python/Node available, FastAPI/uvicorn preinstalled).
- A dedicated app service principal identity to read/write data and call Databricks APIs.
- A reverse proxy that forwards a known set of `X-Forwarded-*` user identity headers to your app (useful for attribution).
- Optional user authorization (OBO) in preview (via `x-forwarded-access-token`) if you later need user-scoped reads.
- A supported way to control outbound traffic via Network Connectivity Configurations (NCC) and network policies when you later integrate with Power BI/Fabric APIs.

---

## What the portal does

### Core outcomes (user value)

1. **Status & Health (MVP)**
   - Global "green/yellow/red/unknown".
   - Per platform tiles:
     - last successful update
     - freshness vs SLA
     - active warnings/incidents
   - Drill-down history and "last failure" diagnostics.

2. **Manual status messages (comms)**
   - Banner messages with time windows, severity, affected platforms.
   - Maintenance notices, incident updates, release notes.

3. **Ticket intake (Delta-only ticketing)**
   - Incidents/bugs: structured submission + comments + workflow state machine.
   - Improvements: feature requests + voting + workflow state machine.
   - "My platform" requests: service-catalog-lite templates (access/onboarding/change).

4. **Docs + business glossary**
   - Git-backed markdown docs rendered in-app.
   - Delta-backed glossary with stewardship fields + search.

5. **Roadmap (Delta-only)**
   - Curated roadmap items, Now/Next/Later, linked to requests.

---

## Target architecture

### Runtime + packaging

Recommended MVP: single origin app (FastAPI serves the React build as static assets).

- No external hosting dependency for the SPA.
- Avoids CORS complexity.
- Keeps "one internal URL" truly single URL.
- Avoids runtime npm install needs (important if outbound is restricted).

Databricks Apps runtime specifics that matter for planning:

- OS: Ubuntu 22.04; Python 3.11; Node.js 22.16.
- Default compute: 2 vCPU / 6GB memory (configurable in beta).
- Default env vars include `DATABRICKS_APP_PORT`, `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`.

### Data flow ("no external calls at request time")

- Scheduled ingestion job(s) run on a cadence (not the app).
- They call:
  - Databricks APIs / logs / warehouse health sources (your choice).
  - Power BI/Fabric APIs (once networking + auth is defined).
- Jobs write normalized results to Delta tables (`status_results`, etc.).
- The portal reads those Delta tables to render status.

This keeps the app fast; failures show up as "stale/unknown" rather than user-facing timeouts.

### Networking for external APIs (Power BI/Fabric)

When you enable outbound calls from ingestion jobs or the app, you'll likely need:

- NCC (stable egress) + network policies (domain allowlist / egress restriction).
- If you restrict egress, plan allowlists for:
  - Microsoft Entra token endpoints (login).
  - Power BI / Fabric API domains.
  - Optional: package registries if you still build dependencies at runtime.

---

## Identity & authorization model

### App identity (service principal)

Databricks Apps provides each app with a dedicated service principal identity and injects:

- `DATABRICKS_CLIENT_ID` + `DATABRICKS_CLIENT_SECRET` for M2M OAuth.
- `DATABRICKS_HOST` for workspace targeting.

This is perfect for your "overall information reads" and shared writes (tickets, comments, votes).

Key implication: the app SP must be granted access to:

- the Unity Catalog tables it reads/writes
- any SQL warehouse it uses for queries

### User attribution (headers)

Databricks Apps forwards a specific set of headers from its reverse proxy:

- `X-Forwarded-User`, `X-Forwarded-Email`, `X-Forwarded-Preferred-Username`, etc.

Practical recommendation for MVP:

- Require `X-Forwarded-User` or `X-Forwarded-Email` for write operations (submit ticket, vote, comment).
- If missing, return 401/403 rather than silently attributing to the app SP.

### Optional later: On-behalf-of-user (OBO)

Databricks supports user authorization (currently public preview) where the user's access token is forwarded in headers and the app can act with user permissions.

For your current plan (no user-permissioned reads), you can defer OBO. But design your API/auth middleware so you can add it later without rewriting everything.

---

## Status ingestion: recommended pattern

### Suggested ingestion sources

Databricks health (choose one path now):

- Workspace APIs (cluster/job/warehouse states).
- Job run logs for pipelines.
- SQL Warehouse health endpoints / query history / system tables.

Power BI:

- For dataset/semantic model freshness, the Power BI REST API exposes refresh history endpoints (example: "Datasets – Get Refresh History").
- Authentication typically uses a Microsoft Entra app/service principal and tenant settings must allow service principals for API access (details vary by tenant policies).

Fabric:

- Fabric REST APIs exist and service principal support has been introduced; some admin scenarios require enabling service principal auth explicitly.

### Job output contract (what gets written to Delta)

Treat each ingest run as:

1. Write a run record (`status_ingestion_runs`) at start (RUNNING).
2. Write individual result records (`status_results`) as you compute.
3. Update run record at end (SUCCESS/FAIL + error payload).
4. Optional: compute rollups (`status_rollups`) for fast UI tiles.

### Failure handling states (UI contract)

Define deterministic UI behavior:

- Healthy: last success within SLA threshold.
- Degraded: late vs SLA (warning threshold).
- Down/Critical: beyond critical threshold, or known failure.
- Unknown: no recent data + ingestion failure OR never ingested.

This avoids confusing "green but stale" scenarios.

---

## Delta-only backend: ticketing model

Because Delta doesn't enforce referential integrity like an OLTP database, the simplest robust approach is:

**Option A (recommended): current state + events**

- `work_items` (current state for fast reads).
- `work_item_events` (append-only audit log of every change).
- `comments` (append-only).
- `votes` (enforced uniqueness in code via `MERGE`).

This gives you:

- Auditability by design.
- Concurrency safety (events append; current state updated with optimistic checks).
- Easy "history" views later.

**Option B: pure event-sourcing**

- Only events; derive current state via views/materialized rollups.
- More complex queries, but simplest write path.

Either works. For an MVP that needs lists and filters, Option A is typically the best tradeoff.

---

## Recommended core schema (agent-friendly)

Below is a minimal-but-complete schema blueprint that maps directly to your modules and solves the missing FK/retention/versioning gaps.

### 1) Platform definitions

- `platforms`
  - `platform_id` (string, PK)
  - `name`, `domain` (databricks/powerbi/fabric), `owner_group`, `sla_profile_id`
  - `is_active`, `created_at/by`, `updated_at/by`

### 2) Status

- `status_checks`
  - `check_id` (PK)
  - `platform_id` (logical FK)
  - `check_type` (freshness/availability/quality)
  - `sla_minutes`, `warn_after_minutes`, `crit_after_minutes`
  - `enabled`, `owner`, `version`, `created_at/by`, `updated_at/by`
- `status_results` (append-only time series)
  - `result_id` (PK)
  - `check_id`, `platform_id`
  - `measured_at`, `status` (green/yellow/red/unknown)
  - `observed_value`, `message`, `error_payload`
  - `ingestion_run_id`
- `status_ingestion_runs`
  - `ingestion_run_id` (PK)
  - `source` (databricks/powerbi/fabric)
  - `started_at`, `ended_at`, `state` (RUNNING/SUCCESS/FAIL), `error_summary`
- `status_messages`
  - `message_id` (PK)
  - `severity`, `title`, `body_md`
  - `start_at`, `end_at`
  - `platform_tags` (array)
  - `published_state`, `created_at/by`, `updated_at/by`

### 3) Work intake (incidents, improvements, service requests)

- `work_items`
  - `item_id` (PK)
  - `item_type` (INCIDENT / IMPROVEMENT / PLATFORM_REQUEST)
  - `platform_id`, `service`, `environment`, `severity`
  - `title`, `description_md`, `tags`
  - `state`, `assigned_to`, `priority`, `due_at` (optional)
  - `version` (int) for optimistic concurrency
  - audit columns
- `work_item_events` (append-only)
  - `event_id` (PK)
  - `item_id`
  - `event_type` (CREATE / STATE_CHANGE / EDIT / ASSIGN / TAG / CLOSE / REJECT)
  - `old_state`, `new_state`
  - `payload` (json)
  - `created_at/by`
- `comments`
  - `comment_id` (PK)
  - `item_id`
  - `body_md`
  - audit columns
- `votes`
  - `item_id`
  - `user_id` (from forwarded headers)
  - `weight` (default 1)
  - audit columns
  - logical uniqueness: (`item_id`, `user_id`) enforced in API layer

### 4) Docs + glossary

- Docs: Git-backed markdown rendered by the app (no Delta required unless you want indexing).
- `glossary_terms`
  - `term_id` (PK)
  - `term`, `definition_md`, `steward`, `domain`, `status` (active/deprecated)
  - `related_assets` (array / json)
  - audit columns

### 5) Roadmap

- `roadmap_items`
  - `roadmap_id` (PK)
  - `theme`, `status`, `target_quarter`, `description_md`
  - `linked_item_ids` (array)
  - audit columns

### 6) RBAC / access control (don't skip this)

- `role_bindings`
  - `principal` (user id/email or group name)
  - `role` (Viewer/Contributor/Triager/Admin/ServiceOwner)
  - `platform_id` (nullable = global)

This creates a simple, explicit authorization layer for the API.

---

## Best path forward (minimize risk early)

### Step 1: Build the walking skeleton (Phase 0)

Goal: app deploys, reads/writes Delta, shows a basic page.

- FastAPI running on `DATABRICKS_APP_PORT`.
- React SPA served by FastAPI (single origin).
- Create UC schema + minimal tables: `platforms`, `status_messages`, `work_items`, `comments`.
- Auth middleware:
  - read `X-Forwarded-User`/`Email`
  - deny writes if missing identity
- Basic endpoints: `/api/v1/me`, `/api/v1/platforms`, `/api/v1/messages`, `/api/v1/work-items`.
- Add `/api/v1/healthz` for ops readiness checks.

### Step 2: Status MVP without Power BI first (Phase 1 core)

Goal: deliver value even if Power BI/Fabric is blocked.

- Ingestion job for Databricks-side checks only.
- Populate `status_results` + `status_ingestion_runs`.
- Front page tiles + drilldown + manual status banners.

### Step 3: Power BI/Fabric feasibility spike (parallel to Phase 1)

Goal: decide the viable integration approach early.

- Confirm tenant-level prerequisites:
  - API permissions + service principal enablement.
- Confirm outbound connectivity approach (NCC / allowlists).
- Implement one "vertical slice":
  - Call Power BI "Get Refresh History".
  - Write normalized refresh status to Delta.
- For Fabric admin/update APIs, confirm service principal auth enablement requirements.

### Step 4: Ticketing MVP (Phase 2)

Goal: real internal support workflows.

- Implement `work_items` + `work_item_events` + `comments` + `votes`.
- State machines + permissions.
- UI lists, detail views, filters, pagination.
- Rate limiting / basic spam control (even if lightweight).

### Step 5: Docs + glossary (Phase 3)

Goal: reduce support load via self-service.

- Docs rendering pipeline (Git → packaged content, or runtime pull if network allows).
- Glossary CRUD + search + term pages.

### Step 6: Hardening (Phase 4+)

Goal: operational maturity.

- RBAC admin UI.
- Audit trails + structured logs.
- Alerting on ingestion failure + portal errors.
- Attachments (as pointers to Volumes/ADLS) + notification hooks.

---

## Decision checklist (pick defaults early)

1. **SPA deployment model**
   - Bundle React build into the app package (recommended for MVP).
   - Host SPA separately (adds CORS + extra deployment surface).
2. **API versioning**
   - Use `/api/v1/...` from day 1 (recommended).
   - No versioning (requires strict backward compatibility discipline).
3. **Identity requirements for writes**
   - Require `X-Forwarded-User` or `X-Forwarded-Email` for submissions/votes/comments (recommended).
   - Allow "anonymous as app SP" (makes auditing and abuse control hard).
4. **RBAC model**
   - Define roles now (Viewer, Contributor, Triager, Admin, ServiceOwner).
   - Decide: role bindings via Entra group snapshot vs manual table vs Databricks groups.
5. **Status SLA & aggregation rules**
   - SLA defined in `status_checks` and editable by admins (recommended).
   - Global status = max severity OR weighted rollup (choose one).
6. **Status retention**
   - Decide time-series retention (e.g., 30/90/180 days) + rollups beyond that.
7. **Job failure UX**
   - Show stale last-success + "unknown" after TTL (recommended).
   - Hard error state.
8. **Power BI/Fabric integration approach**
   - Power BI: which APIs/endpoints, scope (per workspace vs tenant admin), service principal model.
   - Fabric: which items you care about; whether admin APIs are needed (and thus enablement).
9. **Networking prerequisites**
   - Will NCC + network policies be ready in Phase 1?
   - If not, treat Power BI/Fabric as Phase 1b with a stubbed UI section.
10. **Ticket data modeling**
   - Unified `work_items` table with `item_type` (recommended).
   - Separate incidents / requests / platform_requests tables.
11. **Docs sourcing & safety**
   - Package docs at build time (recommended under egress restrictions).
   - Decide markdown sanitization model (trusted repo only vs sanitize HTML).
