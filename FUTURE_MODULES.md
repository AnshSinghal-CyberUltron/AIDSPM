# Extension map after the read-only MVP

This file maps the **full agreed product scope** to later contracts. Endpoint names and tables below are **proposals**, not stable OpenAPI paths, implemented controls, or complete source-specific designs. Version each module after its capability spike and negative tests. Keep the G1 operator API useful while adding modules independently.

## 1. AI lifecycle and repeating DSPM cycle

Every applicable AI lifecycle stage has the same eight DSPM checks: **C01 Discover**, **C02 Classify**, **C03 Map lineage and access**, **C04 Assess and prioritize**, **C05 Enforce and remediate**, **C06 Verify**, **C07 Monitor and audit**, **C08 Respond and improve**. A stage/check pair must be `supported`, `planned`, `unsupported`, `not_applicable` with reason, or `unknown`; do not fabricate 112 passing checks.

| ID | Lifecycle stage | Minimum versioned object/evidence to add |
| --- | --- | --- |
| A01 | Purpose and ownership | Use case, accountable owner, approved purpose, users, retention, retirement owner |
| A02 | Acquire data and providers | Source rights, permitted uses, provider terms, transfer region, reviewer/expiry |
| A03 | Discover and collect | Dataset/source inventory, coverage receipt, source permissions |
| A04 | Prepare and label | Transformation manifest, inherited labels and ACL/purpose constraints |
| A05 | Select model and architecture | Provider/model capability, license, endpoint, fallback, retention choice |
| A06 | Train and adapt | Input manifest, authorization, training identity, checkpoints/adapters |
| A07 | Build RAG, agents and tools | Index/chunk provenance, delegation, tools, memory and source ACL epoch |
| A08 | Evaluate and approve | Version-bound privacy/quality/adversarial evaluations and gate decision |
| A09 | Package, release and deploy | Code/image/model/data/index/prompt/tool/policy digests and observed deployment |
| A10 | Infer and act | Input/output and retrieval/tool boundary decisions and delivery receipts |
| A11 | Monitor and respond | Drift, blind interval, finding, incident and response evidence |
| A12 | Change and improve | Impact analysis and reapproval on changed artifacts/config |
| A13 | Retire AI system | Stop new activity, drain work, disable routes/identities, enumerate copies |
| A14 | Retain, dispose and verify | Legal holds, deletion/retention ledger, backup restore and residual model risk |

Proposed tables: `use_cases`, `stage_instances` keyed by use-case + stage + version,
`stage_control_checks` keyed by stage-instance + C01–C08 + scope, and `gate_decisions`
bound to exact artifact/configuration digests. Required fields on each check: status, owner,
evidence IDs, limitations, observed time, expiry and the test run ID for any `verified` state.
`not_applicable` requires a reviewer and reason; no blanket skip for a training-capable system.
Proposed API: `/api/v1/use-cases`, `/use-cases/{id}/stages`, `/stages/{id}/checks`,
`/releases/{id}/gates`. Read-only posture data may populate C01–C04; do not emit an
enforcement/verification pass until C05/C06 actually execute.

## 2. Six forms of Shadow AI and code-to-cloud

| Form | Signal connectors to qualify | Evidence/limit |
| --- | --- | --- |
| Coding agents | Endpoint/IDE inventory, repo config, provider audit | Installed/configured/observed active are different |
| MCP clients/servers/tools | Approved client config, tool schema, server identity, call events | Tool description does not prove downstream privilege |
| Direct/indirect LLM calls | Repository/static dependency scan, proxy traces, provider audit | Code candidate is not executed deployment |
| Agentic applications | Agent registry, runtime spans, tool decisions, identities | Model-directed action must be observed or tested |
| Managed cloud AI | AWS/Azure/GCP resource and invocation/audit connectors | Actual event schemas, license/permissions and lag vary |
| AI-enabled SaaS | IdP grants, SaaS feature/audit APIs, SSE/browser signals | SSO proves app use, not every AI prompt or vendor internals |

Use one tenant-scoped graph for **AI Resources**, **Supporting Resources**, and **SCA findings**.
Add typed records for `repositories`, `commits`, `ci_builds`, `image_digests`,
`deployments`, `cloud_resources`, `workload_identities`, `model_endpoints`, `mcp_servers`,
`tool_bindings`, `packages`, `sbom_components`, and `sca_findings` as connector gates pass.
`graph_edges` must reference evidence with origin, source event/version, time, expiry and
strength (`candidate`, `configured`, `observed`, `source_verified`); the UI cannot promote
an edge merely because adjacent nodes exist.

Proposed API families: `/connectors` and `/connectors/{id}/capabilities`, `/observations`
for **authenticated producer ingest**, `/ai-resources`, `/supporting-resources`,
`/supply-chain/findings`, `/graph/paths`, `/deployments/{id}/lineage`. Ingest binds tenant
from producer credentials; supplied `tenant_id`, trace or actor fields are untrusted
claims until correlated. Deduplicate on producer/source event ID and revision. Cap graph
depth/fan-out and show truncated or missing links. One verified repo → build → image →
deployment → workload identity → model-call path is the first code-to-cloud gate.

## 3. G2 protected RAG: exact data obligations

Add `source_acl_snapshots` (source, revision, collected/expires), `source_grants`
(principal/group, resource, action, conditions, decision, evidence), `chunks`
(source asset version, index version, offsets, payload/reference, label/purpose inheritance),
`chunk_acl_links`, `policy_revisions`, `authorization_decisions`, and a separate
source database with pgvector for the deterministic fixture. Product catalog references
chunk payloads; it need not become a raw document warehouse.

Proposed internal API is authenticated **per workload**, with trusted delegated user
context and a source candidate/version. Result includes `allowed/denied/unknown`,
enforced action, reason, source ACL revision, policy revision, evaluated/expiry time and
request ID. Do not accept `groups`, `tenant_id` or `delegated_user_id` from an untrusted
application body as authority. Purpose (`retrieve`, `train`, `export`) is part of the
decision; permission to read does not authorize training or external model disclosure.

Required execution order: validate identities → resolve source ACL/policy → constrain
candidate set → retrieve only allowed chunks → inspect **assembled** model input → call
approved model → inspect result before delivery. Check revocation, stale/unknown ACL,
cross-tenant cache and concurrent changes. Verify that Bob's forbidden payroll content
is absent from actual model-fixture input, output, citations, cache and logs.

## 4. Runtime, agents, policy and safe remediation

| Area | Proposed API / table families | Mandatory failure test |
| --- | --- | --- |
| Policy | `/policies`, `/policies/{id}/revisions`, `/simulate`, `/activate`; `policy_revisions`, `policy_decisions` | Old approval not reused after policy/asset version changes |
| Input/output | `/runtime/requests`, `/runtime/receipts`; `boundary_receipts` | Retry, fallback, direct SDK and unsupported attachment bypass explicit |
| Agent/MCP | `/agents`, `/tools`, `/bindings`, `/delegations`; `tool_schema_versions`, `delegations` | Service identity cannot widen human authority; changed schema denied |
| Remediation | `/remediations/preview`, `/{id}/approve`, `/{id}/execute`, `/{id}/verify`, `/{id}/compensate`; `remediation_plans`, `approvals`, `step_receipts` | Concurrent source change causes no write; partial apply not green |
| Audit/OTel | `/events`, `/control-evidence`, `/exports`; append-only event/evidence and export ledgers | Canary absent from logs/traces/export; missing telemetry is a blind interval |

Runtime receipts distinguish `observed`, `simulated`, `enforced`, and `verified`. A provider
HTTP 200 is not an allowed release to the user. In strict streaming mode, detection must
occur before releasing forbidden bytes. Unsupported input shapes fail or are visibly out
of supported coverage, per application policy. OpenTelemetry compatibility means using
documented telemetry semantics and exporting sanitized signals to customer-selected
collectors; it does not justify recording raw prompts by default.

Remediation state machine: `draft → previewed → pending_approval → approved → executing →
partially_applied/applied → verifying → verified/failed`. Bind approval to tenant, exact
target, expected source revision, diff digest, permitted actions and expiry. Use separate
write credentials. After execution, read back source state and retest the original forbidden
path **and** legitimate access. Compensation is explicit and may fail; an API 202 means
accepted for work, not “fixed.” Destructive steps cannot be auto-run simply because a risk
score is high.

## 5. Retirement, offline operation and assurance

Proposed `retirement_plans`, `derivative_ledgers`, `deletion_receipts`, `legal_holds`,
`restore_reconciliations`, and `offline_bundle_manifests` record each data/source/index/
cache/provider file and trained artifact separately. APIs may plan and inspect these jobs;
they must not call a model “unlearned” because a source document was deleted. Retired
workloads cannot accept new managed execution; known residual copies and inaccessible
provider interiors remain visible.

An air-gappable deployment packages pinned/signed OCI images, Python dependencies,
rules and model artifacts for an offline environment, with local OIDC, DB, audit/OTel,
updates and licensing strategy. Test with outbound network denied, clock skew, bundle
tampering, rollback attempts, backup restoration and stale evidence. A Lovable-hosted
preview is never proof of offline operation.

Compliance screens can map controls to actual evidence, scope, owner, expiry and exceptions.
SOC 2/HIPAA/GDPR language is a design objective or scoped evidence mapping until a formal
assurance process establishes the relevant claim. GPU/token/cost metrics depend on actual
telemetry exposed by customer infrastructure or providers; show unavailable otherwise.

## 6. Risk-register mapping for implementation review

| Risk IDs | Dominant area | First relevant gate |
| --- | --- | --- |
| R01–R10 | Shadow AI, copies, coverage, classification, data rights, public grants and encryption | G1 plus qualified discovery connectors |
| R11–R22 | Transforms, training, privacy, model artifacts and supply chain | Lifecycle A04–A08 plus D/SCA |
| R23–R38 | RAG, stale ACLs, runtime, prompt/output, agents, MCP, inference and availability | G2/P3/P4 |
| R39–R46 | Artifact-bound approval, deployment, missing telemetry, SaaS opacity and governance | Release/monitoring gates |
| R47–R54 | Incident scope, remediation, retirement, copies, backups and holds | Response/retirement gates |
| R55–R60 | Scanner compromise, evidence replay, offline tamper/clock, races and exports | Cross-cutting hardening and offline gate |

Keep the exact R01–R60 descriptions and tests in the master lifecycle document. For each
supported risk, record a connector/platform/version scope, control, negative test, evidence
expiry and residual limitation. A risk-register row is **not** a detected incident.
