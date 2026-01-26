# Milestone M0 - Walking skeleton

Goal
- Replace the Flask todo app with the FastAPI + React skeleton that matches AGENTS.md.
- Ensure local dev works end to end with stub data and repeatable tests.

Exit criteria
- FastAPI serves /api/v1/healthz and /api/v1/readyz.
- React SPA loads from the same origin and can call the API.
- Local dev Mode A works with documented steps.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M0.T1 - Repo layout and baseline tooling
Goal: Align repo layout with AGENTS.md while preserving legacy Flask code.
Context: Repo has app.py and templates/ at root; AGENTS.md expects backend/ and frontend/.
Dependencies: None.
Constraints:
- Do not delete legacy Flask; archive it.
- Keep runtime path clear of Flask (no app.yaml pointing to app.py).
Steps:
- Create backend/, frontend/, jobs/, infra/, docs/ directories.
- Move legacy Flask app to legacy/ (or archive/) and add a short note.
- Move app.yaml to infra/app.yaml and point to the new FastAPI entrypoint (placeholder ok until M0.T2).
- Add placeholder backend/pyproject.toml (uv) and frontend/package.json.
- Update AGENTS.md layout section only if the structure deviates.
Acceptance:
- Repo tree matches AGENTS.md or AGENTS.md is updated.
- Flask code is not on the runtime path.
Testing:
- Quick import check for backend package once created.
Files:
- infra/app.yaml
- legacy/ (app.py, templates/)
- backend/pyproject.toml
- frontend/package.json
- AGENTS.md (if needed)
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T2 - FastAPI skeleton and request identity
Goal: Stand up the FastAPI app with health and identity basics.
Context: Backend must run locally and use /api/v1 routes.
Dependencies: M0.T1.
Constraints:
- Use /api/v1 prefix and AGENTS.md error shape.
- DEV_USER/DEV_EMAIL only when DATABRICKS_HOST is not set.
Steps:
- Create backend/app/main.py with FastAPI app instance and router wiring.
- Add /api/v1/healthz and /api/v1/readyz endpoints (readyz can be stubbed initially).
- Add request id propagation (X-Request-Id or generated).
- Implement identity extraction from forwarded headers and DEV override.
Acceptance:
- /api/v1/healthz returns 200.
- /api/v1/readyz returns 200 or 503 with a stubbed check.
- Identity extraction works with forwarded headers and DEV override.
Testing:
- Unit tests for health and identity extraction.
Files:
- backend/app/main.py
- backend/app/api/v1/health.py
- backend/app/auth/ (middleware/deps)
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T3 - SPA serving and React scaffold
Goal: Create a React SPA scaffold and mount it in FastAPI for single origin.
Context: Frontend should proxy /api in dev and be served by FastAPI in prod.
Dependencies: M0.T1, M0.T2.
Constraints:
- Keep /api routes API-only; SPA catch-all serves index.html.
Steps:
- Create frontend/ with Vite React and a minimal router shell.
- Add routes: Status, Tickets, Docs, Glossary, Roadmap.
- Add an API client module with base URL and request id handling.
- Configure Vite proxy for /api to backend.
- Mount the built SPA in FastAPI for production.
Acceptance:
- SPA renders a navigation shell and placeholder pages.
- API calls from SPA reach FastAPI in local dev.
Testing:
- Frontend smoke test and API client unit test.
Files:
- frontend/ (Vite scaffold)
- backend/app/main.py (static mount)
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T4 - Data access adapters and local fixtures
Goal: Add a data access layer with local fixtures to unblock UI/API development.
Context: Databricks access is not required for M0; use mock data.
Dependencies: M0.T2.
Constraints:
- Keep adapters read-only for external systems.
Steps:
- Define repository interfaces for platforms, status, and work items.
- Implement a local fixture adapter (in-memory or JSON).
- Stub a Databricks adapter interface for later implementation.
Acceptance:
- API endpoints can return stub data without Databricks access.
Testing:
- Unit tests for local adapter reads.
Files:
- backend/app/db/ (adapters)
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T5 - Local dev configuration and docs
Goal: Make Mode A setup explicit and repeatable.
Context: New devs should be able to run frontend and backend locally.
Dependencies: M0.T2, M0.T3.
Constraints:
- Do not add secrets to repo.
Steps:
- Add .env.example with required variables.
- Document Mode A steps in README or docs/.
- Note DEV_USER/DEV_EMAIL behavior for local dev.
Acceptance:
- A new dev can run Mode A with only local commands.
Testing:
- Manual: start both servers and load the SPA.
Files:
- backend/.env.example
- docs/ or README.md
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T6 - Baseline test harness
Goal: Provide backend and frontend test harnesses.
Context: Tests must run locally before PRs.
Dependencies: M0.T2, M0.T3.
Constraints:
- Keep tooling minimal and fast.
Steps:
- Add pytest, ruff, and mypy config for backend.
- Add a frontend test runner (vitest or jest).
- Add minimal test examples to confirm wiring.
Acceptance:
- All tests pass locally with stub data.
Testing:
- Run backend unit tests and frontend test runner.
Files:
- backend/pyproject.toml
- frontend/package.json
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T7 - Config and environment settings
Goal: Centralize backend configuration for local and Databricks Apps.
Context: Need env-driven settings and sensible defaults.
Dependencies: M0.T2.
Constraints:
- DEV overrides only when DATABRICKS_HOST is not set.
Steps:
- Implement a Settings class (pydantic-settings or equivalent).
- Include DATABRICKS_APP_PORT with local fallback to 8000.
- Add DEV_USER/DEV_EMAIL toggles with correct guard.
- Align .env.example with settings fields.
Acceptance:
- Settings load cleanly with no env vars set.
- DEV override is disabled when DATABRICKS_HOST is present.
Testing:
- Small config import test.
Files:
- backend/app/core/config.py
- backend/.env.example
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T8 - Auth middleware and /api/v1/me
Goal: Provide user identity plumbing and a me endpoint.
Context: Writes require user attribution; reads may be anonymous.
Dependencies: M0.T7.
Constraints:
- Use forwarded headers and DEV overrides per AGENTS.md.
Steps:
- Add auth middleware to parse forwarded headers into request state.
- Add get_current_user and get_optional_user dependencies.
- Add /api/v1/me endpoint returning current user info.
Acceptance:
- /api/v1/me returns user info with headers and 401 without identity.
Testing:
- Unit tests for header parsing and DEV override behavior.
Files:
- backend/app/auth/
- backend/app/api/v1/me.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T9 - Database layer scaffold
Goal: Provide DB connection scaffolding for Databricks SQL Warehouse.
Context: Real warehouse access will come later; mock mode must work now.
Dependencies: M0.T4.
Constraints:
- Imports should work without Databricks credentials.
Steps:
- Add DB connection module and base query utilities.
- Add a placeholder Databricks SQL connector adapter with pooling hooks.
- Keep local dev working via mock adapters.
Acceptance:
- DB modules import cleanly without Databricks credentials.
Testing:
- Unit tests for mocked query paths.
Files:
- backend/app/db/
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T10 - Error handling and response format
Goal: Standardize API error responses to the AGENTS.md shape.
Context: All endpoints must return consistent error payloads.
Dependencies: M0.T2.
Constraints:
- Include request_id in all errors.
Steps:
- Add custom exception classes and handlers.
- Ensure 404 and 422 errors use the standard error shape.
- Register handlers on the FastAPI app.
Acceptance:
- Error responses match the standard shape across endpoints.
Testing:
- API tests for 404 and validation errors.
Files:
- backend/app/core/exceptions.py
- backend/app/core/error_handlers.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T11 - Logging setup
Goal: Structured logging with request correlation.
Context: Logs must include request id and user when present.
Dependencies: M0.T2, M0.T8.
Constraints:
- JSON output in production, readable logs in dev.
Steps:
- Add logging configuration with env-driven log level.
- Add request logging middleware for path, status, latency, request_id, user.
Acceptance:
- Logs include request_id and user when present.
Testing:
- Manual log verification with sample requests.
Files:
- backend/app/core/logging.py
- backend/app/main.py
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T12 - CI workflow
Goal: Add CI for lint, tests, and builds.
Context: CI should run on PRs and pushes.
Dependencies: M0.T6.
Constraints:
- Keep steps aligned with AGENTS.md commands.
Steps:
- Add GitHub Actions workflow for backend lint/tests.
- Add frontend lint/tests/build steps with caching.
Acceptance:
- Workflow passes on a clean branch.
Testing:
- Run the same commands locally.
Files:
- .github/workflows/ci.yml
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T13 - Local dev scripts
Goal: Add convenience scripts for repeatable local workflows.
Context: Reduce manual steps for dev, test, format, build.
Dependencies: M0.T6.
Constraints:
- Scripts should work on macOS zsh.
Steps:
- Add scripts/dev.sh, scripts/test.sh, scripts/format.sh, scripts/build.sh.
- Document script usage briefly.
Acceptance:
- Scripts run without manual edits.
Testing:
- Run scripts/test.sh and scripts/dev.sh locally.
Files:
- scripts/
- docs/ or README.md
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.

## M0.T14 - RBAC skeleton (early)
Goal: Add RBAC schema and service stubs without enforcement.
Context: Full enforcement comes in M4; skeleton unblocks early integration.
Dependencies: M0.T2.
Constraints:
- No endpoint enforcement in this task.
Steps:
- Add role_bindings schema SQL with required audit columns.
- Implement an RBAC service interface for role lookup and checks.
- Add permission dependency stubs for later endpoint enforcement.
- Add mock role bindings for local dev/testing.
Acceptance:
- RBAC service can resolve roles from mock data.
- No endpoint enforcement changes yet.
Testing:
- Unit tests for role resolution and permission helpers.
Files:
- backend/app/services/rbac_service.py
- backend/app/auth/permissions.py
- backend/app/db/schemas/role_bindings.sql
- backend/tests/
Done means:
- Update INDEX.md emoji for M0 if status changes; note deviations.
