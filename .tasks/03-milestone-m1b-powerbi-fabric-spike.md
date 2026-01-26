# Milestone M1b - Power BI and Fabric feasibility spike

Goal
- Validate whether Power BI and Fabric data can be ingested with the planned auth and networking model.

Exit criteria
- A documented decision on feasibility, auth model, and network requirements.
- At least one successful ingestion proof of concept written to Delta.

Agent guidance
- Keep tasks limited to two layers; split if needed.
- Update INDEX.md emoji when task completion changes milestone status.

## M1b.T1 - Prerequisites and decision record
Goal: Confirm tenant, permissions, and network prerequisites.
Context: Power BI/Fabric access requires tenant settings and network allowlists.
Dependencies: M1.T2 (ingestion job scaffold) recommended.
Constraints:
- Document decisions; do not hardcode secrets.
Steps:
- Confirm tenant settings for service principal API access.
- Identify required API permissions and scopes.
- Define networking requirements (NCC, allowlists).
- Capture decisions in a short ADR or docs note.
Acceptance:
- Decision record exists and is referenced in docs.
Testing:
- None.
Files:
- docs/adr-*.md or docs/notes/
Done means:
- Update INDEX.md emoji for M1b if status changes; note deviations.

## M1b.T2 - Power BI refresh history ingestion POC
Goal: Prove Power BI API ingestion into Delta.
Context: Use a single endpoint to validate auth and data normalization.
Dependencies: M1b.T1.
Constraints:
- Ingestion runs outside the web app.
Steps:
- Implement a job that calls Power BI Get Refresh History.
- Normalize response into status_results.
- Store raw payload as needed for debugging.
Acceptance:
- Delta tables show Power BI results for at least one workspace.
Testing:
- Unit test normalization with mocked payloads.
Files:
- jobs/src/
- jobs/tests/
Done means:
- Update INDEX.md emoji for M1b if status changes; note deviations.

## M1b.T3 - Fabric API feasibility check
Goal: Verify Fabric API reachability and auth.
Context: Determine whether Fabric scope is viable.
Dependencies: M1b.T1.
Constraints:
- Use a minimal, safe read-only endpoint.
Steps:
- Call a simple Fabric endpoint with service principal auth.
- Record response and feasibility in the ADR.
Acceptance:
- Clear go/no-go decision for Fabric scope.
Testing:
- Basic smoke call in a dev environment (if permitted).
Files:
- docs/adr-*.md or docs/notes/
Done means:
- Update INDEX.md emoji for M1b if status changes; note deviations.
