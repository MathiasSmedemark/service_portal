# Project task plan - Internal Support and Status Portal

Purpose
- Deliver the full portal scope in phased milestones, starting with a walking skeleton.
- Keep local development and testing working at every milestone.
- Require automated and manual tests per task because this is a vibe coded build.

References
- AGENTS.md
- project.md
- INDEX.md

Process rules
- Do not start a milestone until the prior milestone exit criteria are met.
- Every task must include automated tests and a short manual verification checklist.
- Keep API under /api/v1 and match the error shape defined in AGENTS.md.
- No external calls at request time. Use jobs for ingestion.
- Keep request handlers read-only from external systems.
- Split any task that touches more than two layers (backend, frontend, jobs, infra, docs).
- Keep INDEX.md updated with emoji state as tasks progress.
- If a task expands beyond its scope, split it and update this plan.

Agent task format
- Task: <ID and title>
- Goal: <one sentence>
- Context: <why it matters, current state>
- Dependencies: <tasks or decisions required first>
- Constraints: <AGENTS.md rules, special requirements>
- Steps: <clear, ordered steps>
- Acceptance: <how to know it is done>
- Testing: <commands or checks>
- Files: <expected files to touch>
- Done means: <INDEX.md update and any notes>

Milestones
- M0: Walking skeleton (FastAPI + React + local dev) and repo layout.
- M1: Status MVP (Databricks only) with ingestion job and dashboard.
- M1b: Power BI/Fabric feasibility spike (parallel, optional gate).
- M2: Ticketing MVP (incidents, improvements, platform requests).
- M3: Docs and glossary MVP.
- M4: Roadmap, RBAC admin, and hardening.

Definition of done for any task
- Code matches AGENTS.md constraints and project.md scope.
- Automated tests added and documented.
- Manual local run steps documented and verified.
- No secrets or hardcoded credentials committed.
- Update docs or AGENTS.md if the repo layout or runtime behavior changes.
- INDEX.md status updated and deviations noted.

Exit criteria per milestone
- M0: app runs locally in Mode A and serves a basic SPA with working API.
- M1: status dashboard shows real data from Delta tables and ingestion job works.
- M1b: Power BI/Fabric ingestion path validated and documented.
- M2: ticketing workflows usable end-to-end with RBAC enforcement.
- M3: docs and glossary are usable with search and pagination.
- M4: roadmap and admin functions work, logs are structured, and tests cover critical paths.
