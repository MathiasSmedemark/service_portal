Project: Internal Support & Status Portal (Azure Databricks Apps)

Purpose

Provide one internal URL where platform users can:
	•	See current platform health (Databricks + Power BI/Fabric) and data freshness
	•	Submit incidents/bugs and improvement requests
	•	Submit “my platform” service requests (access/change/onboarding)
	•	Read user-facing documentation and a business glossary
	•	See roadmap and status messages

Hosted as a Databricks App using FastAPI + React (SPA), with a Delta-only backend workflow for now.

⸻

Architecture (decisions reflected)

Runtime & UI
	•	Databricks App runs a FastAPI service that:
	•	Serves REST endpoints for status and ticketing
	•	Serves the built React SPA as static assets
	•	This aligns with “bring-your-own-framework” approaches and existing FastAPI-on-Apps recipes and starters.  ￼	
	❗ NEEDS DECISION:
	•	React SPA build & deployment: Will you build as part of CI/CD and bundle into the App package, or serve from external storage?
	•	CORS policy: Specify allowed origins if SPA is served separately.
	•	API versioning: Will you version endpoints (/v1/status) or rely on backward compatibility?
Authentication & identity
	•	The app runs under the Databricks App service principal for “overall information” reads; Databricks injects the service principal credentials via environment variables DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET.  ￼
	•	User attribution for submissions and voting is captured from request context (commonly forwarded user identity headers such as X-Forwarded-Email / X-Forwarded-User in Apps setups).  ￼
	•	OBO (on-behalf-of-user) is explicitly not required now, but can be enabled later if you ever want user-permissioned reads; OBO uses X-Forwarded-Access-Token when enabled.  ￼	
	❗ CRITICAL GAPS:
	•	Header validation: How do you validate/trust X-Forwarded-* headers? Are they injected by Databricks security layer or user-provided?
	•	Fallback identity: What happens if user headers are missing? Deny or use service principal?
	•	Entra group membership: For user_platform_map, how fresh/reliable is this? Query live or snapshot?
Status ingestion pattern (your preference)
	•	The portal does not call external APIs at request time.
	•	A scheduled job (every ~5 min) writes normalized results into Delta status tables; the app reads those tables.
	
	❗ CRITICAL GAPS:
	•	Power BI/Fabric integration unclear: Which APIs will you use? Admin APIs? REST? How do you authenticate?
	
	❗ NEEDS DECISION:
	•	Will NCC/network policies be in place before Phase 1? This blocks Power BI integration feasibility.
	•	Databricks status source: Are you querying workspace APIs, SQL Warehouse health APIs, or job logs?
	•	Failure handling: If a job fails/times out, does the app show stale data, or an error state?
	•	Job observability: Where are job execution logs? How will ops detect failed ingestion?
	•	5-min cadence feasibility: For external APIs (Power BI), will 5 min be throttled/blocked? Need to define realistic interval per source.

Networking (parked, but design-ready)
	•	When you later connect to Power BI/Fabric APIs directly (or other services), Databricks Apps supports controlled outbound connectivity via Network Connectivity Configurations (NCC) and network policies.  ￼

⸻

Features to develop (by module)

1) Status & front page (MVP value)

User-facing
	•	Global health indicator (green/yellow/red)
	•	Per-domain/platform tiles:
	•	“Last successful update”
	•	“Freshness vs SLA”
	•	“Current incidents / warnings”
	•	Drill-down “Status details” page: check history, last failures, owners

Backend	
	❗ NEEDS CLARIFICATION:
	•	SLA definition: How are thresholds defined? Hard-coded, per-platform config, or user-editable?
	•	Health aggregation logic: If one platform fails, is global status red? Or weighted by importance?
	•	Data retention: How long do you keep status_results? (affects query performance and cost)
	•	Caching strategy: How often does the front page query vs cache? Stale acceptable threshold?	•	status_checks definitions (what to measure, SLA thresholds)
	•	status_results time-series results (computed by jobs)
	•	status_rollups (optional materialized rollups for fast UI)
	
	❗ NEEDS DECISION:
	•	Who can create/publish? Admins only? Service owners? Approval workflow needed?
	•	Can messages be edited after publish, or create new versions?
	•	Archival: Keep old messages visible in history, or hide after end date?2) Status messages (manual comms)
	•	Create/edit/publish “banner” messages (maintenance, incident updates, release notes)
	•	Scheduled visibility windows (start/end)
	•	Severity + affected services tagging

3) Submissions: incidents/bugs
	•	Submit incident with structured fields:
	•	service, platform_id, severity, environment, descript
	
	❗ NEEDS DECISION:
	•	State transitions: Can any user change state? Or only assigned/triage owner?
	•	Spam prevention: Rate limiting per user? Required fields validation?
	•	Notifications: When should incident creator/owner be notified? (Phase 4 says "if required" but unclear)
	•	Duplicate detection: Any validation/warning if similar incident exists?
	•	Attachment support: Mentioned in Phase 4—will you support or explicitly disallow for MVP?ion, repro steps
	•	Comment thread
	
	❗ NEEDS DECISION:
	•	Voting visibility: Can users see vote counts before voting, or blind voting?
	•	Vote weighting: Are all votes equal in MVP, or do you want role-based weights from day 1?
	•	Rejection clarity: When rejected, is a reason/comment required?
	•	State machine: New → Triaged → In Progress → Resolved → Closed
	•	Audit columns on every change (created/updated/by/at)

4) Submissions: improvements (feature request	
	❗ CRITICAL GAPS:
	•	Routing/assignment: How do requests get routed to the right team? Auto-tag based on service, or manual?
	•	SLA tracking: Should these have SLOs/resolve-by dates like incidents?
	•	Workflow: Are approval workflows required (e.g., manager approval before fulfillment)?
	•	Integration: How does fulfillment happen? Manual ticket creation in external system (Jira, Azure DevOps)?
	•	Cost implications: For provisioning requests—how do you prevent runaway resource requests?	•	Submit improvement request with category + expected value
	•	Voting/rating (one vote per user per item; optional weighted roles later)
	•	State machine: New → Under Review → Planned → In Delivery → Done / Rejected

5) “My platform” requests (service catalog-lite)
	•	Request types (templates):
	•	access to dataset/report
	
	❗ NEEDS DECISION:
	•	Curation model: Who maintains roadmap? Single owner or open contributions?
	•	Linking to requests: How do you link improvement #123 to roadmap item #5? Bidirectional or just lookup?
	•	Visibility: Can all users see all roadmap items, or is there access control per theme/platform?
	•	Accuracy: How do you prevent roadmap from drifting from actual delivery (ADO sync in Phase 5)?
	•	onboarding a new source
	•	refresh cadence change
	•	workspace/project provisioning (if applicable)
	•	Each request type enforces required fields
	
	❗ CRITICAL GAPS:
	•	Git integration mechanism: Which repo? Auto-deploy on push (webhooks) or manual pull? Staging/approval workflow?
	•	Markdown safety: How do you prevent malicious markdown/HTML? Sanitize or trusted repo only?
	•	Glossary sourcing: Is this manually entered or integrated with a metadata store (Data Catalog)?
	•	Search strategy: Full-text search for glossary terms? Fuzzy matching or exact?
	•	Staleness handling: Glossary terms not updated—when do you deprecate/archive?
	•	Same tables/states/comments/audit approach

6) Roadmap page (Delta-only)
	•	roadmap_items curated table:
	•	theme, status, target quarter, linked requests
	•	Views: Now / Next / Later

7) Docs + Business glossary
	•	Git-backed markdown rendered in-app (docs)
	•	Delta-backed glossary:
	•	term, definition, steward/owner, related assets

8) Lineage (low priority, but “combined when users see it”)
	•	Phase later: show “Data asset” page that can aggregate:
	•	Databricks lineage view (where available)
	•	Fabric/Power BI lineage link (or summary)
	•	Implement as a single “Asset” experience rather than separate lineage systems.

⸻

Delta-only data model (initial)

Core tables (minimum):
	•	status_checks, status_results, status_messages
	•	incidents, requests (improvements), platform_requests
	•	comments
	•	votes
	•	roadmap_items
	•	platforms (definition of platform_id)
	•	user_platform_map (user → platform(s) mapping) or derive from Entra group snapshots

All tables include:
	•	id, platform_id, state, created_at, created_by, updated_at, updated_by

❗ CRITICAL MISSING DETAILS:
	•	Primary/Foreign keys: No referential integrity defined. Missing foreign keys: incidents → platforms, votes → requests, comments → parent (incident/request), etc.
	•	Cascading deletes: If a platform is deleted, what happens to incidents/requests? Soft delete or cascade?
	•	Retention policy: How long do you keep resolved incidents / closed requests? Archive to cold storage?
	•	Versioning: If status_checks SLA changes, how do you handle existing results? New version field?
	•	User_platform_map freshness: Query live Entra groups or maintain snapshot? Sync frequency?
	•	Data location: Which catalog + schema? Unity Catalog metastore name?
	•	Indexes/partitioning: How are tables optimized for time-range queries (e.g., "last 7 days of incidents")?
	•	Soft deletes: Should you implement soft deletes for auditability rather than hard deletes?

⸻

CROSS-CUTTING CONCERNS (Not yet addressed)

Role-Based Access Control (RBAC)
	❗ CRITICAL MISSING: The entire document lacks permission definitions.
	•	Can all users see all platforms? Incidents? Roadmap?
	•	Who can create incidents vs. improvements vs. service requests?
	•	Who can change state? Who can edit/delete?
	•	Admin users: How do you identify them (Entra group, hardcoded list, Databricks workspace admins)?
	•	Suggestion: Define roles early (Viewer, Contributor, Incident Triager, Admin, Service Owner).

Performance & Scalability
	•	No query optimization strategy defined.
	•	Caching: In-app (Flask), Redis, or materialized views?
	•	Pagination: Large lists (100+ open incidents) need pagination; not mentioned.
	•	Real-time updates: Is the app pull-based (user refreshes) or push (WebSocket/polling)?
	•	Concurrent writes: How do you handle simultaneous state transitions on same incident?

Monitoring & Observability
	•	No logging strategy for the portal itself.
	•	Health checks: How do ops know if the portal is down/degraded?
	•	Metrics: Request latency, error rate, job execution times?
	•	Alerting: Which failures trigger alerts?

Error Handling & Resilience
	•	What if status ingestion job fails? Does app show "unknown" or cached data?
	•	What if Git webhook for docs fails? Does old docs get served?
	•	Timeout strategy: What's the max query time before timeout?
	•	Graceful degradation: If one feature breaks, can others still work?

⸻

Phase 0 — Foundation (week 1–2)
	•	App skeleton: FastAPI + React SPA served from FastAPI
	•	Auth wiring:
	•	service principal auth via injected env vars  ￼
	•	user attribution capture for submissions/votes (headers/context)  ￼
	•	Delta schema + core tables + basic admin page for platform definitions

Phase 1 — Status MVP (week 2–4)
	•	Implement status ingestion jobs → status_results every ~5 minutes
	•	Front page + status drilldown + manual status messages
	•	Power BI/Fabric refresh status integrated via job → Delta (details depend on your API approach and network policy later)

Phase 2 — Ticketing MVP (week 4–6)
	•	Incidents: create + list + detail + comments + state transitions
	•	Improvements: create + list + voting + basic prioritization views
	•	“My platform requests”: request templates + routing tags

Phase 3 — Docs + Glossary (week 6–8)
	•	Markdown renderer + navigation
	•	Glossary search + term pages + stewardship fields
	•	Link glossary terms to datasets/reports (via a lightweight asset registry)

Phase 4 — Operational hardening (when needed)
	•	Role-based admin views (moderation, spam control, editing)
	•	Attachments (ADLS/Volumes pointers)
	•	Notifications (Teams/email) if required
	•	Performance: caching/materialized rollups

Phase 5 — Enhancements (future)
	•	Hybrid with ADO (sync tickets both ways)
	•	Combined lineage/asset pages; OBO if you later need user-scoped reads  ￼