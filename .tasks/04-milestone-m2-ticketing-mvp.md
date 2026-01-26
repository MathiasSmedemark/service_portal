# Milestone M2 - Ticketing MVP

Goal
- Provide incident, improvement, and platform request workflows backed by Delta tables.

Exit criteria
- Users can create, view, comment, and vote on items.
- State transitions are audited with optimistic concurrency.
- RBAC is enforced for write actions.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M2.T1 - Delta schema for work items
Goal: Define work_items and work_item_events tables.
Context: Work items are the core ticket entity with auditability.
Dependencies: M0 complete.
Constraints:
- Include audit columns and version for concurrency.
Steps:
- Create DDL for work_items and work_item_events.
- Add item_type and event_type enums in models.
- Document state machine assumptions.
Acceptance:
- DDL is ready and documented.
Testing:
- Validate DDL syntax in a dev UC workspace if available.
Files:
- backend/app/db/schemas/work_items.sql
- backend/app/db/schemas/work_item_events.sql
- backend/app/models/work_item.py
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T2 - Work items API (list, detail, create)
Goal: Expose core work item endpoints.
Context: Basic ticket workflows require list, detail, and create.
Dependencies: M2.T1, M0.T8.
Constraints:
- Writes require user identity.
- Pagination required for list endpoint.
Steps:
- Implement GET list with filters and pagination.
- Implement GET detail with related data (events or counts).
- Implement POST create with validation and audit fields.
Acceptance:
- API supports list, detail, and create with proper error shape.
Testing:
- API tests for create, read, pagination.
Files:
- backend/app/api/v1/work_items.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T3 - Comments and votes API
Goal: Add comments and votes endpoints.
Context: Comments are append-only; votes are idempotent.
Dependencies: M2.T1, M0.T8.
Constraints:
- Votes must be unique per (item_id, user_id).
Steps:
- Implement /work-items/{id}/comments endpoints.
- Implement /work-items/{id}/vote endpoint with MERGE semantics.
Acceptance:
- Comments append correctly and votes are idempotent.
Testing:
- API tests for duplicate votes and comment creation.
Files:
- backend/app/api/v1/comments.py
- backend/app/api/v1/votes.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T4 - Ticketing UI (list, detail, create)
Goal: Build the core ticketing UI flows.
Context: Users need to browse, view, and create tickets.
Dependencies: M2.T2, M2.T3.
Constraints:
- Keep API interactions in hooks or API modules.
Steps:
- Build list page with filters and pagination.
- Build detail page with timeline, comments, and voting.
- Build create form with validation and redirect.
Acceptance:
- Users can complete core ticket flows in local dev.
Testing:
- Frontend tests for list rendering and form validation.
Files:
- frontend/src/pages/
- frontend/src/components/tickets/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T5 - Workflow state transitions
Goal: Enforce state transitions and role checks.
Context: State changes must follow defined workflows.
Dependencies: M2.T2.
Constraints:
- Use expected_version for optimistic concurrency.
Steps:
- Implement state change endpoint with expected_version.
- Enforce role checks for triage and state changes.
Acceptance:
- Invalid transitions return 400 and conflicts return 409.
Testing:
- API tests for allowed and blocked transitions.
Files:
- backend/app/api/v1/work_items.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T6 - Work item service layer and state machines
Goal: Centralize work item business logic.
Context: State machines differ by item type.
Dependencies: M2.T1.
Constraints:
- Keep logic in services, not in routers.
Steps:
- Implement WorkItemService create/update/transition logic.
- Define per-type state machines and validation rules.
- Enforce optimistic concurrency checks in service layer.
Acceptance:
- State transitions follow defined rules per item type.
Testing:
- Unit tests for service logic and state machines.
Files:
- backend/app/services/work_item_service.py
- backend/app/services/state_machines.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T7 - Work item updates and event history
Goal: Support updates and event history endpoints.
Context: Detail view needs a full audit trail.
Dependencies: M2.T2, M2.T6.
Constraints:
- Events are append-only and ordered chronologically.
Steps:
- Add PATCH endpoint for editable fields.
- Add /work-items/{id}/events endpoint.
- Ensure events include payload details for changes.
Acceptance:
- Work item detail includes full event history.
Testing:
- API tests for update and events endpoints.
Files:
- backend/app/api/v1/work_items.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T8 - Ticket list UI
Goal: Build a filterable list view.
Context: Users need to discover and triage tickets quickly.
Dependencies: M2.T2.
Constraints:
- Support filters and sorting.
Steps:
- Add filters for type, state, platform, and search.
- Add sort options (created_at, votes, priority).
- Add pagination controls and loading/error states.
Acceptance:
- List page is navigable and filterable in local dev.
Testing:
- Component tests for filters and table rendering.
Files:
- frontend/src/pages/WorkItemList.tsx
- frontend/src/components/tickets/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T9 - Ticket detail UI
Goal: Build the ticket detail view with actions.
Context: Users need to act on tickets and see history.
Dependencies: M2.T7.
Constraints:
- Use markdown rendering with sanitization for descriptions.
Steps:
- Render metadata, description, and current state.
- Add comment list and comment form.
- Add vote button and event timeline.
- Add state transition controls.
Acceptance:
- Users can view and act on a ticket in local dev.
Testing:
- Component tests for detail view and actions.
Files:
- frontend/src/pages/WorkItemDetail.tsx
- frontend/src/components/tickets/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T10 - Ticket create form UI
Goal: Build ticket creation flow.
Context: Different ticket types require different fields.
Dependencies: M2.T2.
Constraints:
- Validate required fields before submit.
Steps:
- Add type selector with type-specific fields.
- Add markdown editor for description.
- Add validation and redirect to detail on success.
Acceptance:
- Users can create tickets end-to-end in local dev.
Testing:
- Component tests for form validation.
Files:
- frontend/src/pages/CreateWorkItem.tsx
- frontend/src/components/tickets/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T11 - Rate limiting for write endpoints
Goal: Add basic anti-spam protections.
Context: Protect create/comment/vote from abuse.
Dependencies: M2.T2, M2.T3.
Constraints:
- In-memory rate limiting is acceptable for MVP.
Steps:
- Add a rate limiter utility with per-endpoint limits.
- Return 429 with Retry-After on limit exceed.
- Make limits configurable via env vars.
Acceptance:
- Excess requests are throttled per user identity.
Testing:
- Unit tests for limiter behavior.
Files:
- backend/app/core/rate_limit.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T12 - Concurrency conflict handling
Goal: Surface optimistic concurrency conflicts in UI.
Context: Users need clear guidance on version conflicts.
Dependencies: M2.T5.
Constraints:
- API returns 409 with current version.
Steps:
- Ensure API returns 409 with current version payload.
- Add frontend conflict modal and retry guidance.
- Display version in detail view.
Acceptance:
- Users can recover cleanly from conflict errors.
Testing:
- API tests for 409 payload and UI tests for modal.
Files:
- backend/app/services/work_item_service.py
- frontend/src/components/common/ConflictModal.tsx
- backend/tests/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T13 - Navigation and routing
Goal: Integrate tickets into app navigation.
Context: App needs consistent navigation across sections.
Dependencies: M0.T3, M2.T4.
Constraints:
- Keep nav accessible and responsive.
Steps:
- Add navigation links and active states.
- Add breadcrumbs on detail pages.
- Ensure mobile responsive behavior.
Acceptance:
- Navigation works across Status, Tickets, Docs, Glossary, Roadmap.
Testing:
- Manual navigation checks in local dev.
Files:
- frontend/src/components/common/Navigation.tsx
- frontend/src/components/common/Breadcrumbs.tsx
- frontend/src/App.tsx
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T14 - End-to-end ticket flow test
Goal: Validate full ticket lifecycle with integration tests.
Context: Ensure create/comment/transition flow works end-to-end.
Dependencies: M2.T2, M2.T5.
Constraints:
- Use mock or test database; no external calls.
Steps:
- Create tests that cover create, comment, transition, and events.
- Include conflict scenario coverage.
Acceptance:
- E2E ticket tests pass in CI.
Testing:
- Run backend E2E tests.
Files:
- backend/tests/e2e/
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.

## M2.T15 - Mock data for tickets
Goal: Extend mock data for local ticketing flows.
Context: Local dev needs realistic ticket scenarios.
Dependencies: M0.T4.
Constraints:
- Toggle via USE_MOCK_DATA.
Steps:
- Add mock work items across types and states.
- Add mock comments and votes.
- Support scenario toggles via env vars.
Acceptance:
- Local dev can render ticket lists and details with mock data.
Testing:
- Manual: verify ticket pages with USE_MOCK_DATA enabled.
Files:
- backend/app/db/mock_data.py
Done means:
- Update INDEX.md emoji for M2 if status changes; note deviations.
