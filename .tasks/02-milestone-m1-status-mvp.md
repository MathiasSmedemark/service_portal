# Milestone M1 - Status MVP (Databricks only)

Goal
- Deliver a functional status dashboard backed by Delta tables and a Databricks ingestion job.

Exit criteria
- Ingestion job writes to status tables.
- API returns status data with pagination.
- SPA shows global and per-platform status tiles.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M1.T1 - Delta schema for status
Goal: Define Delta schemas for status-related tables.
Context: Status data must be stored in Unity Catalog with audit fields.
Dependencies: M0 complete.
Constraints:
- Use required columns from AGENTS.md (id, audit fields, state where required).
- Use UC naming: <catalog>.<schema>.<table>.
Steps:
- Create DDL for platforms, status_checks, status_results, status_ingestion_runs, status_messages.
- Store schemas under backend/app/db/schemas/.
- Document any assumptions in docs/ or the schema files.
Acceptance:
- DDL reviewed and ready for execution in UC.
Testing:
- Validate DDL syntax in a dev UC workspace if available.
Files:
- backend/app/db/schemas/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T2 - Databricks ingestion job (status only)
Goal: Implement a scheduled job that writes status results.
Context: No external calls at request time; ingestion is async.
Dependencies: M1.T1.
Constraints:
- Write status_ingestion_runs RUNNING -> SUCCESS/FAIL.
- Keep ingestion logic isolated in jobs/.
Steps:
- Scaffold jobs/ with Python entrypoint and requirements.
- Implement run lifecycle and status_results writes.
- Normalize results into a consistent schema.
- Add error handling with failure summaries.
Acceptance:
- Job writes sample data into Delta and marks run state correctly.
Testing:
- Unit test normalization logic with fixtures.
Files:
- jobs/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T3 - Status API endpoints (base)
Goal: Expose basic status data via API endpoints.
Context: UI needs platform and status results lists.
Dependencies: M1.T1, M0.T2.
Constraints:
- Use /api/v1 and standard error shape.
- Pagination required for list endpoints.
Steps:
- Implement /api/v1/platforms, /api/v1/status-results, /api/v1/status-messages.
- Add pagination and stable ordering (created_at desc).
- Use adapters that support mock data.
Acceptance:
- Endpoints return data for both local fixtures and Databricks adapter.
Testing:
- API tests for pagination and ordering.
Files:
- backend/app/api/v1/
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T4 - Status dashboard UI
Goal: Build the main status dashboard UI.
Context: Users need global and per-platform status at a glance.
Dependencies: M1.T3.
Constraints:
- Handle empty and stale data states gracefully.
Steps:
- Build dashboard page with global health and platform tiles.
- Add drilldown entry points and message banner slots.
- Implement loading and error states.
Acceptance:
- UI matches API data and handles empty or stale data.
Testing:
- Component tests for empty, healthy, degraded, and unknown states.
Files:
- frontend/src/pages/StatusDashboard.tsx
- frontend/src/components/status/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T5 - Local test data and demo scripts
Goal: Make local demoing possible without Databricks.
Context: Local dev should show realistic status scenarios.
Dependencies: M0.T4.
Constraints:
- Do not add secrets to fixtures.
Steps:
- Extend local fixtures to cover status scenarios.
- Add a demo script or docs for seeding local data.
Acceptance:
- Local Mode A can display realistic status data.
Testing:
- Manual: run local servers and confirm status views render.
Files:
- backend/app/db/mock_data.py
- docs/ or README.md
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T6 - Platform CRUD and models
Goal: Add platform models and CRUD endpoints.
Context: Platforms are top-level entities for status and ownership.
Dependencies: M1.T1, M0.T2.
Constraints:
- Admin-only create/update (RBAC stub acceptable until M4).
Steps:
- Add platform models and service layer.
- Implement GET list and GET detail endpoints.
- Implement POST create with validation.
Acceptance:
- Platforms can be listed and retrieved by id.
Testing:
- API tests for list and detail endpoints.
Files:
- backend/app/models/platform.py
- backend/app/services/platform_service.py
- backend/app/api/v1/platforms.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T7 - Status checks configuration API
Goal: Manage status_checks definitions.
Context: Checks define SLA thresholds and ownership.
Dependencies: M1.T1, M0.T2.
Constraints:
- Validate warn < crit and values > 0.
Steps:
- Add status_check models and service layer.
- Implement list and detail endpoints with platform filters.
- Add admin create/update endpoints.
Acceptance:
- Checks can be listed, filtered, and validated.
Testing:
- API tests for status_checks endpoints.
Files:
- backend/app/models/status_check.py
- backend/app/services/status_check_service.py
- backend/app/api/v1/status_checks.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T8 - Status results query endpoints
Goal: Support filtered status results queries.
Context: UI needs time range and latest results per check.
Dependencies: M1.T1, M0.T2.
Constraints:
- Pagination and stable ordering required.
Steps:
- Add filters for platform_id, check_id, and time range.
- Add /api/v1/status-results/latest for most recent per check.
Acceptance:
- Latest and filtered queries return expected results.
Testing:
- API tests for filters and latest endpoint.
Files:
- backend/app/api/v1/status_results.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T9 - Status aggregation and summary
Goal: Compute global and per-platform status rollups.
Context: Dashboard needs a single health summary.
Dependencies: M1.T7, M1.T8.
Constraints:
- Status semantics per project.md (green/yellow/red/unknown).
Steps:
- Implement aggregation logic based on SLA thresholds and freshness.
- Add /api/v1/status/summary endpoint.
- Handle edge cases (no data, stale ingestion).
Acceptance:
- Summary endpoint reflects correct global and platform states.
Testing:
- Service tests for aggregation logic and edge cases.
Files:
- backend/app/services/status_service.py
- backend/app/api/v1/status.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T10 - Status messages workflow and admin endpoints
Goal: Manage manual status messages with lifecycle states.
Context: Messages are published as banners with time windows.
Dependencies: M1.T1, M0.T2.
Constraints:
- Only published messages in active window are public.
Steps:
- Implement draft/published/archived workflow.
- Add admin create/update endpoints.
- Filter public messages by time window and published state.
Acceptance:
- Active messages return only current window and published state.
Testing:
- API tests for message lifecycle and filtering.
Files:
- backend/app/models/status_message.py
- backend/app/services/message_service.py
- backend/app/api/v1/messages.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T11 - Ingestion runs API
Goal: Expose ingestion run status for diagnostics.
Context: UI needs last run status and failures.
Dependencies: M1.T1, M1.T2.
Constraints:
- Include error_summary for failures.
Steps:
- Implement list and latest endpoints for ingestion runs.
- Add filters by source if needed.
Acceptance:
- UI can retrieve recent run status per source.
Testing:
- API tests for ingestion run endpoints.
Files:
- backend/app/models/ingestion_run.py
- backend/app/api/v1/ingestion_runs.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T12 - Frontend platform detail view
Goal: Add platform detail page with history and failures.
Context: Users need drilldown from dashboard tiles.
Dependencies: M1.T8, M1.T9.
Constraints:
- Keep API usage behind hooks or API client modules.
Steps:
- Add route and page for /platforms/:id.
- Render history chart and failure details.
- Add time range selector and breadcrumbs.
Acceptance:
- Platform detail page loads with history data.
Testing:
- Component tests for history and detail views.
Files:
- frontend/src/pages/PlatformDetail.tsx
- frontend/src/components/status/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T13 - Frontend message banners
Goal: Render and manage status message banners.
Context: Active messages should appear prominently.
Dependencies: M1.T10.
Constraints:
- Dismissal should persist in session storage.
Steps:
- Add severity-based styling and stacking behavior.
- Implement dismiss with session storage.
- Link to affected platforms where applicable.
Acceptance:
- Banners display and can be dismissed in session.
Testing:
- Component tests for banner behavior.
Files:
- frontend/src/components/status/MessageBanner.tsx
- frontend/src/pages/StatusDashboard.tsx
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T14 - Mock data toggle for status
Goal: Enable mock data for local dev scenarios.
Context: Devs should switch between realistic status scenarios.
Dependencies: M0.T4.
Constraints:
- Toggle via USE_MOCK_DATA env var.
Steps:
- Add USE_MOCK_DATA toggle to backend data layer.
- Provide scenarios (all green, degraded, unknown).
- Document usage in local dev instructions.
Acceptance:
- Local dev can switch between mock scenarios.
Testing:
- Manual: set USE_MOCK_DATA and verify outputs.
Files:
- backend/app/db/mock_data.py
- docs/ or README.md
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.

## M1.T15 - End-to-end status flow test
Goal: Validate the full status flow with integration tests.
Context: Ensure ingestion -> API summary logic works end-to-end.
Dependencies: M1.T2, M1.T9.
Constraints:
- Use mock or test database; no external calls.
Steps:
- Create a backend E2E test that seeds data and queries summary.
- Cover healthy, degraded, critical, and unknown cases.
Acceptance:
- E2E status test passes in CI.
Testing:
- Run backend E2E tests.
Files:
- backend/tests/e2e/
Done means:
- Update INDEX.md emoji for M1 if status changes; note deviations.
