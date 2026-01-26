# Milestone M3 - Docs and glossary

Goal
- Provide self-service docs and a searchable glossary backed by Delta.

Exit criteria
- Docs are rendered from markdown.
- Glossary terms are searchable with pagination.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M3.T1 - Docs pipeline (decision and setup)
Goal: Choose build-time docs bundling and set the baseline.
Context: Runtime fetch is discouraged; bundle docs at build time.
Dependencies: M0.T3.
Constraints:
- No raw HTML unless sanitized.
Steps:
- Decide build-time bundling approach.
- Add markdown rendering with sanitization.
- Add docs routing skeleton in the SPA.
Acceptance:
- Docs render in the SPA and are safe to display.
Testing:
- Frontend tests for markdown rendering and sanitization.
Files:
- frontend/src/pages/Docs.tsx
- frontend/src/components/docs/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T2 - Glossary Delta schema
Goal: Define glossary_terms table.
Context: Glossary is Delta-backed and needs audit columns.
Dependencies: M0 complete.
Constraints:
- Include required audit columns and term fields.
Steps:
- Create DDL for glossary_terms.
- Document schema assumptions.
Acceptance:
- DDL is documented and ready for execution.
Testing:
- Validate DDL syntax in dev UC if available.
Files:
- backend/app/db/schemas/glossary_terms.sql
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T3 - Glossary API
Goal: Implement glossary CRUD and search endpoints.
Context: UI needs list, detail, and search with pagination.
Dependencies: M3.T2.
Constraints:
- Use stable ordering and pagination limits.
Steps:
- Add /api/v1/glossary list, detail, and search endpoints.
- Add admin create/update/delete endpoints (RBAC stub ok).
Acceptance:
- API returns consistent results with pagination.
Testing:
- API tests for search, pagination, and detail retrieval.
Files:
- backend/app/api/v1/glossary.py
- backend/app/models/glossary.py
- backend/tests/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T4 - Glossary UI
Goal: Build glossary list and detail views.
Context: Users need search and term details in the SPA.
Dependencies: M3.T3.
Constraints:
- Keep API usage in hooks or API modules.
Steps:
- Build glossary search page with filters.
- Build term detail view with related assets.
- Display steward and status fields.
Acceptance:
- Users can find and read glossary terms in local dev.
Testing:
- Frontend tests for search and detail views.
Files:
- frontend/src/pages/Glossary.tsx
- frontend/src/components/glossary/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T5 - Docs content structure
Goal: Define docs folder structure and authoring conventions.
Context: Docs live in docs/ with navigation metadata.
Dependencies: M0 complete.
Constraints:
- Keep content in markdown with frontmatter.
Steps:
- Create docs/ structure with sample pages.
- Add docs/_sidebar.json for navigation tree.
- Add README for authoring guidelines.
Acceptance:
- Docs structure is present and documented for contributors.
Testing:
- Manual: verify sample docs load in local dev.
Files:
- docs/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T6 - Docs build pipeline
Goal: Bundle docs at build time for offline use.
Context: Avoid runtime network calls for docs.
Dependencies: M3.T5.
Constraints:
- Build step should run before frontend build.
Steps:
- Add a build script to parse markdown and frontmatter.
- Generate a docs manifest JSON for the frontend.
- Wire the script into the frontend build pipeline.
Acceptance:
- Docs manifest is generated on build.
Testing:
- Run build script and validate output JSON.
Files:
- scripts/build-docs.js or scripts/build_docs.py
- frontend/package.json
- frontend/src/generated/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T7 - Docs rendering UI
Goal: Render docs pages with navigation.
Context: Users need a sidebar and readable content layout.
Dependencies: M3.T6.
Constraints:
- Sanitize markdown output.
Steps:
- Implement docs index and content pages.
- Render markdown with syntax highlighting.
- Add previous/next navigation.
Acceptance:
- Docs pages render with sidebar navigation.
Testing:
- Frontend component tests for docs rendering.
Files:
- frontend/src/pages/Docs.tsx
- frontend/src/components/docs/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T8 - Docs search
Goal: Add client-side search across docs.
Context: Docs are bundled, so search is local.
Dependencies: M3.T6.
Constraints:
- Debounce input; no API calls.
Steps:
- Build a search index from the docs manifest.
- Add a docs search UI with snippets and highlights.
- Implement keyboard navigation if feasible.
Acceptance:
- Search returns relevant docs without API calls.
Testing:
- Frontend tests for search behavior.
Files:
- frontend/src/components/docs/DocsSearch.tsx
- scripts/build-docs.js or scripts/build_docs.py
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T9 - Glossary admin UI
Goal: Provide a basic admin UI for glossary management.
Context: Admins need to add and edit glossary terms.
Dependencies: M3.T3.
Constraints:
- Gate access with RBAC.
Steps:
- Add admin route and forms for create/edit.
- Add status toggle and delete confirmation.
Acceptance:
- Admin can manage glossary terms in local dev.
Testing:
- Manual admin flow checks.
Files:
- frontend/src/pages/admin/GlossaryAdmin.tsx
- frontend/src/components/admin/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.

## M3.T10 - Mock data for docs and glossary
Goal: Provide local mock data for glossary and docs.
Context: Local dev should work without Delta access.
Dependencies: M0.T4.
Constraints:
- Keep mock content realistic but minimal.
Steps:
- Add mock glossary terms with varied domains and statuses.
- Ensure docs samples are included in build output.
Acceptance:
- Local dev shows glossary content without Delta.
Testing:
- Manual: verify glossary pages with USE_MOCK_DATA enabled.
Files:
- backend/app/db/mock_data.py
- docs/
Done means:
- Update INDEX.md emoji for M3 if status changes; note deviations.
