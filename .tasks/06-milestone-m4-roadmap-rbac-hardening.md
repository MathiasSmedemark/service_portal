# Milestone M4 - Roadmap, RBAC, and hardening

Goal
- Add roadmap and admin features and harden the app for production use.

Exit criteria
- Roadmap is editable and visible.
- RBAC is enforced consistently across backend and UI.
- Logs and health endpoints are production ready.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M4.T1 - Roadmap schema and API
Goal: Add roadmap_items table and API endpoints.
Context: Roadmap items are curated and linked to work items.
Dependencies: M0 complete.
Constraints:
- Include audit columns and stable ordering.
Steps:
- Create roadmap_items schema.
- Implement /api/v1/roadmap list and detail endpoints.
Acceptance:
- Roadmap data is visible via API.
Testing:
- API tests for list and detail endpoints.
Files:
- backend/app/db/schemas/roadmap_items.sql
- backend/app/api/v1/roadmap.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T2 - Roadmap UI
Goal: Build roadmap page with Now/Next/Later views.
Context: Users need a clear view of roadmap phases.
Dependencies: M4.T1.
Constraints:
- Link roadmap items to work items where applicable.
Steps:
- Build roadmap page with sections and filters.
- Add links to related work items.
Acceptance:
- Users can browse roadmap and open linked items.
Testing:
- Frontend tests for filters and rendering.
Files:
- frontend/src/pages/Roadmap.tsx
- frontend/src/components/roadmap/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T3 - RBAC admin UI
Goal: Provide admin UI for role bindings and finalize data access wiring.
Context: RBAC skeleton exists from M0; M4 wires real data and UI.
Dependencies: M0.T14, M4.T7.
Constraints:
- Admin-only access.
Steps:
- Wire role_bindings data access to real storage.
- Add admin UI to view/add/remove role bindings.
- Add admin endpoint tests for role binding CRUD.
Acceptance:
- Admins can view, add, and remove role bindings.
Testing:
- API tests for admin RBAC allow and deny cases.
Files:
- backend/app/api/v1/role_bindings.py
- frontend/src/pages/admin/RBACAdmin.tsx
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T4 - Observability and reliability
Goal: Harden logging and readiness checks for production.
Context: M0 provides baseline logging; M4 tightens production behavior.
Dependencies: M0.T10, M0.T11.
Constraints:
- Use standard error shape and include request_id in logs.
Steps:
- Ensure structured logs include user identity and request ids.
- Implement readiness check for warehouse connectivity.
- Add error reporting with the standard error shape across endpoints.
Acceptance:
- Logs are structured and include key fields.
Testing:
- Unit tests for log context and error shape.
Files:
- backend/app/core/logging.py
- backend/app/api/v1/health.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T5 - Performance and safety hardening
Goal: Enforce pagination and rate limiting defaults.
Context: Prevent abuse and unbounded queries.
Dependencies: M2.T11.
Constraints:
- Default limit 25, max 200 per AGENTS.md.
Steps:
- Enforce limit defaults and max values on all list endpoints.
- Add rate limiting for write endpoints if not already present.
- Document retention policy for time series tables.
Acceptance:
- API behaves safely under load with predictable limits.
Testing:
- API tests for pagination bounds and rate limit behavior.
Files:
- backend/app/api/v1/
- docs/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T6 - End to end tests and runbook
Goal: Validate core user journeys and document a runbook.
Context: E2E coverage is required before production.
Dependencies: M1, M2, M3 complete.
Constraints:
- Use local or test environment; no external calls.
Steps:
- Add a minimal E2E test suite (Playwright or similar).
- Document a runbook for local testing and demo.
Acceptance:
- E2E tests cover status, tickets, and docs flows.
Testing:
- Run E2E tests locally.
Files:
- frontend/tests/e2e/ or tests/e2e/
- docs/runbook.md
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T7 - RBAC core logic and permission matrix
Goal: Define roles, permissions, and enforcement helpers.
Context: Build on the M0 RBAC skeleton.
Dependencies: M0.T14.
Constraints:
- Keep permission checks centralized.
Steps:
- Define a permission matrix for endpoints.
- Extend RBAC service layer with permission evaluation.
- Add permission decorators or dependencies.
Acceptance:
- Permission checks are centralized and testable.
Testing:
- Unit tests for RBAC service and permissions.
Files:
- backend/app/services/rbac_service.py
- backend/app/auth/permissions.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T8 - Apply RBAC across endpoints
Goal: Enforce RBAC on all endpoints.
Context: All read/write/admin endpoints should be protected.
Dependencies: M4.T7.
Constraints:
- 403 responses must use standard error shape.
Steps:
- Apply permissions to all read/write/admin endpoints.
- Update API tests to include role coverage.
Acceptance:
- Unauthorized access is consistently blocked.
Testing:
- API tests for allow and deny scenarios.
Files:
- backend/app/api/v1/
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T9 - Metrics and monitoring hooks
Goal: Expose Prometheus-compatible metrics.
Context: Ops needs basic request and latency metrics.
Dependencies: M0.T2.
Constraints:
- Keep metrics endpoint lightweight.
Steps:
- Add /metrics endpoint.
- Track request counts, latency, and error rates.
- Document metrics usage.
Acceptance:
- Metrics endpoint is reachable in local dev.
Testing:
- Manual: curl /metrics and verify output format.
Files:
- backend/app/core/metrics.py
- backend/app/api/metrics.py
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T10 - Health check improvements
Goal: Expand readiness checks for dependencies.
Context: Readiness should surface warehouse and ingestion status.
Dependencies: M4.T4.
Constraints:
- Keep timeouts configurable.
Steps:
- Add component status to /api/v1/readyz.
- Check warehouse connectivity and ingestion freshness.
- Return per-component latency and status.
Acceptance:
- /readyz returns component status with latencies.
Testing:
- API tests for readyz response shape.
Files:
- backend/app/api/v1/health.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T11 - Ingestion alerting hooks
Goal: Detect and surface ingestion failures or staleness.
Context: Stale ingestion should be observable in logs and readiness.
Dependencies: M4.T10.
Constraints:
- No external calls at request time.
Steps:
- Add a service that computes staleness thresholds.
- Emit structured logs or optional webhook alerts.
- Surface alerts in readiness checks.
Acceptance:
- Stale ingestion produces a structured alert signal.
Testing:
- Unit tests for staleness detection.
Files:
- backend/app/services/alerting_service.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T12 - Performance testing
Goal: Load test key endpoints.
Context: Validate latency and concurrency targets.
Dependencies: M4.T5.
Constraints:
- Document results and bottlenecks.
Steps:
- Add locust or k6 load test scripts.
- Document target thresholds and results.
- Capture bottlenecks and fixes.
Acceptance:
- Load test results are recorded and reviewed.
Testing:
- Run load tests locally.
Files:
- tests/load/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T13 - Security review and hardening
Goal: Complete a security checklist and remediate issues.
Context: Review input validation, XSS, SQL injection, and secrets handling.
Dependencies: M4.T5.
Constraints:
- Do not log secrets.
Steps:
- Validate input handling and parameterized queries.
- Ensure markdown sanitization and XSS protections.
- Verify secrets are not logged.
- Document findings in docs/.
Acceptance:
- Security checklist is completed and stored in docs/.
Testing:
- Manual verification and targeted tests.
Files:
- docs/security-review.md
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T14 - Production configuration and deployment docs
Goal: Finalize Databricks Apps deployment configuration.
Context: Deployment should be documented and reproducible.
Dependencies: M0.T1.
Constraints:
- Secrets must be referenced, not embedded.
Steps:
- Update infra/app.yaml and infra/databricks.yml.
- Document deployment and rollback steps.
- Ensure app config matches runtime requirements.
Acceptance:
- Deployment docs are complete and accurate.
Testing:
- Run databricks bundle validate in a dev environment if available.
Files:
- infra/app.yaml
- infra/databricks.yml
- docs/deployment.md
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T15 - Error tracking integration
Goal: Add optional error tracking for production.
Context: Capture unhandled exceptions with context.
Dependencies: M4.T4.
Constraints:
- Disabled by default in local dev.
Steps:
- Integrate Sentry (or equivalent) with env-based DSN.
- Capture request context on unhandled errors.
- Make integration opt-in via env vars.
Acceptance:
- Errors are reported when DSN is configured.
Testing:
- Manual: trigger a test error with DSN set.
Files:
- backend/app/main.py
- backend/app/core/config.py
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.

## M4.T16 - Documentation update
Goal: Ensure project docs are up to date.
Context: Docs must reflect the actual repo and workflows.
Dependencies: M4.T14.
Constraints:
- Keep AGENTS.md aligned with repo structure.
Steps:
- Update README, AGENTS.md, and troubleshooting docs.
- Ensure API docs and runbooks are current.
Acceptance:
- Documentation matches current repo behavior.
Testing:
- Manual doc review.
Files:
- README.md
- AGENTS.md
- docs/
Done means:
- Update INDEX.md emoji for M4 if status changes; note deviations.
