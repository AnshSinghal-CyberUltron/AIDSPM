# ZeroShield AI Estate Discovery and Code-to-Cloud Security

## Scope and implementation addendum

Version 1.0 | 24 September 2026 | Status: proposed implementation specification

This addendum extends `AI_DSPM_Implementation_Plan_and_Tasks.md`, version 1.0 dated 10 September 2026. The original P0–P7 and T01–T64 identifiers remain unchanged. D01–D22 below are additional tasks, not claims of completed development. No application, connector, customer integration, or security test was executed to produce this document. All commands, APIs, fixtures, performance thresholds, and verification steps described here are contracts to implement and run.

The original plan begins with custom AI applications and RAG, customer-hosted processing, and staged verification. Those decisions remain. This extension adds multi-signal shadow AI discovery, code-to-deployment provenance, supporting-resource inventory, and AI supply-chain analysis. It does not postpone the first working MVP until every cloud, endpoint, and SaaS integration exists.

## 1. Product decision

The product must cover all six requested forms of AI:

1. Sanctioned and unsanctioned coding assistants and agents.
2. MCP servers, tools, and client bindings, including supported desktop and hosted clients.
3. Direct and indirect model calls from application code, frameworks, and proxies.
4. Agents in which model outputs influence tool selection or execution.
5. Applications using managed AI services such as Bedrock, Microsoft Foundry, and Google-hosted AI services.
6. Employees using SaaS products with AI features, including cases where the vendor's underlying model is not visible.

This is now an AI security platform with an AI-DSPM foundation. Its functional layers are estate discovery, posture, supply-chain analysis, data-access analysis, runtime enforcement, and controlled remediation. A single shared evidence graph connects them.

Recommended positioning: **Discover AI across code, cloud, endpoints, and SaaS; trace it to identities and sensitive data; enforce and verify access controls inside the customer's boundary.**

Broad discovery is a prerequisite, not a proven unique selling point. Differentiation remains a product hypothesis until customer pilots establish that ZeroShield's supported authorization, provenance, and remediation workflows are materially better. Do not claim competitors lack a feature solely because it is absent from a public page.

### 1.1 Precise meaning of “cover all of this”

Coverage means a documented connector and detector contract for each supported platform, version, deployment mode, event type, and enforcement path. It does not mean omniscient discovery of all code or vendor-internal AI.

An asset is not automatically “shadow” because it was newly discovered. Keep independent fields for:

- Approval: approved, prohibited, pending review, unknown, or exception with expiry.
- Ownership: known team, unassigned, or disputed.
- Lifecycle: candidate, installed, configured, deployed, observed active, inactive, or retired.
- Evidence: declared, statically detected, observed, authoritatively evaluated, or controlled-test verified.
- Coverage: complete for the declared connector scope, partial, stale, failed, unsupported, or not connected.
- Enforcement: monitored, enforceable, enforced, tested, bypass detected, or unknown.

An installed coding assistant can be approved but unused. A sanctioned SaaS product can have an unapproved AI feature. An agent can be approved for development and prohibited in production. Model these scopes explicitly.

## 2. Three operator views, one underlying graph

| Operator view | Objects and analysis | Why it exists |
| --- | --- | --- |
| A. AI Resources | AI applications, coding-agent installations, logical agents and versions, model endpoints, model artifacts, RAG knowledge bases, vector collections, MCP servers/tools/bindings, guardrails and policies | Answers what AI exists, who owns it, what it can do, and whether it is actually active |
| B. Supporting Resources | Repositories, commits, CI jobs, build attestations, container digests, packages, deployments, VMs, functions, clusters, devices, users, service principals, cloud roles, credentials as references, data stores, network routes | Explains how AI is built, operated, authenticated, and connected to data |
| C. Supply Chain | Package/container vulnerabilities, licenses, provenance, IaC findings, code findings, secrets findings, model/prompt/tool provenance, dependency relationships | Explains what a particular deployed AI version contains and what risks affect that version |

SCA means Software Composition Analysis: analysis of software components and dependencies. It is an analysis capability, not a third mutually exclusive resource class. Its findings attach to resources in A and B. Keep the three UI views, but never create three disconnected inventories.

Data sources, document versions, chunks, labels, and source ACL revisions from the original DSPM plan remain first-class objects. A knowledge base is AI-specific; its underlying bucket or database is a supporting resource; the original sensitive documents retain DSPM identities.

## 3. Discovery coverage matrix

| Required AI form | Primary signals | Supporting signals | Evidence to present | Boundary and negative example |
| --- | --- | --- | --- | --- |
| Coding assistants and coding agents | Customer-approved endpoint/EDR inventory, IDE extensions, installed packages, process ancestry, approved configuration discovery | IdP application access, gateway events, provider audit where available | Device, user, tool/version, approval scope, local/remote models, MCP bindings, last observed activity | A package installation is not active use; unmanaged devices and personal accounts can be invisible |
| MCP attached to desktop or hosted clients | Supported client configurations, administrative APIs/exports, approved server inventories, server/proxy audit, tool manifests | Endpoint processes for local stdio servers; OAuth grant metadata for supported remote servers | Client-to-server binding, transport, tool schema version, auth issuer/audience, downstream resource mapping | Local stdio has no network connection to discover; a tool description does not prove access or harmlessness |
| Direct or indirect LLM calls | Repository AST/rule analysis, SDK and HTTP call patterns, framework adapters, proxy routing config, runtime traces | Package lockfiles, provider audit events, egress telemetry | Code location and commit; candidate provider; requested model alias; observed resolved provider/model when exposed | A dependency is not a call; a call in unused code is not a deployed workload; a proxy hostname is not the final model |
| Agentic applications | Agent definitions, orchestration graphs/configuration, tool registrations, SDK spans and tool-execution events | Deployment inventory and associated workload identities | Agent version, autonomous capabilities, delegated user, tools offered vs invoked, repeated execution steps | A deterministic workflow calling an LLM is not automatically an autonomous agent |
| Managed-cloud AI | Resource inventories, IAM, audit events, invocation metadata, agent/knowledge-base configs, approved diagnostic traces | Billing/usage, image/function deployment metadata, network routes | Account/project/subscription, region, workload, caller identity, model, guardrail attachment, activity | Resource presence is not invocation; audit permissions do not imply prompt/response access |
| AI embedded in SaaS | IdP and OAuth app inventory, SaaS administrator APIs, feature configuration and AI-specific activity logs | Managed browser/SSE metadata, contracts/vendor attestations, customer registration | Product tenant, employee, feature enabled vs used, evidence source, accessible data scopes | Ordinary SaaS login does not prove AI use; proprietary backend code, weights, and prompts may be unknowable |

Every connector must expose what is missing. A silent data source is not a clean data source. Domain catalogs, spend, DNS, and traffic fingerprints help generate candidates; they do not independently prove prompts, model identity, sensitive-data disclosure, or an employee's intent.

### 3.1 Important current platform distinctions

- Microsoft Entra separates interactive users, non-interactive users, service principals, and managed identities in sign-in reporting. Ingest the relevant kinds rather than treating all activity as a human login. These records describe authentication/access context, not complete downstream AI behavior. [Entra sign-in logs](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins).
- Bedrock CloudTrail coverage is operation-specific. Current documentation distinguishes model invocation operations logged as management events from agent and other operations requiring data-event selectors. A single generic “CloudTrail connected” badge is insufficient. [Bedrock CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html).
- Bedrock model invocation logging is a separate facility, disabled by default, with documented endpoint limitations. Inventory/audit discovery should not require enabling full prompt collection. Obtain explicit customer approval before changing logging or collecting content. [Bedrock invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html).
- Microsoft Foundry tracing requires appropriate configuration and access to its telemetry store; custom application logic may need client instrumentation. Treat resource discovery and execution tracing as separate capabilities. [Foundry tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/trace-agent-setup).
- “Gemini logs” is not one connector. Separate Google Cloud AI resource/audit integration, Gemini API/AI Studio project integration, and Gemini-in-Workspace activity. Their tenants, permissions, defaults, available fields, and export mechanisms differ. [Google Cloud audit logging](https://docs.cloud.google.com/vertex-ai/docs/general/audit-logging), [Gemini API logging](https://ai.google.dev/gemini-api/docs/logs-datasets), [Gemini Workspace activity](https://developers.google.com/workspace/admin/reports/v1/appendix/activity/gemini-in-workspace-apps).

## 4. Code-to-cloud correlation

### 4.1 The required chain

For a supported container application, establish these relationships independently:

| Relationship | Preferred evidence | Unacceptable shortcut |
| --- | --- | --- |
| Repository to commit | Repository provider ID and immutable commit ID | Repository display name alone |
| Commit to build | CI run identity, build inputs, verified provenance attestation | Matching branch or timestamp alone |
| Build to artifact | Artifact content digest, attestation subject, trusted builder identity | Mutable image tag |
| Artifact to workload | Actual running container digest, workload UID, cluster/account, deployment interval | Desired deployment spec without checking running state |
| Workload to credential/identity | Platform identity binding plus runtime/token-issuance evidence where available | Source IP behind a shared NAT |
| Workload to proxy/model | Authenticated telemetry, request correlation, proxy routing version, provider receipt when available | URL string in source code |
| Agent/tool to data | Source-specific permission evaluation plus tool bindings and observed source events | Natural-language tool description |
| Source object to vector chunk | Document/version ID, index run, chunk ID, ACL revision and content lineage | Similar document names or embedding similarity |

Build attestations support the source/build/artifact link; they do not by themselves prove what was deployed or called at runtime. Validate the trusted builder, subject digest, and source revision. GitHub documents artifact and SBOM attestations and an offline-verification route. [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).

### 4.2 Worked example

The support-assistant repository at commit `example-commit-A` is built by an approved CI workflow into image digest `sha256:example-A`. A deployment snapshot shows this digest running in a support namespace. It uses workload identity `support-assistant`, calls proxy route `support-default`, and a runtime event resolves that route to an approved model endpoint. Its MCP binding offers `search_cases` and `export_cases`.

DSPM finds that `export_cases` uses a shared service identity with broader access than the requesting employee. The relevant evidence path is now: deployed code version, agent/tool binding, effective downstream identity, source data sensitivity, and observed export attempt.

The operator can ask:

1. Which code version introduced this tool binding?
2. Where is that artifact currently running?
3. Which identities can it assume under known conditions?
4. Which model handled the observed request, including proxy retries/fallbacks?
5. What data is potentially reachable, and what was actually accessed?
6. Which enforcement point can stop this specific action?

If the CI attestation is missing, retain the workload and runtime evidence but show the source linkage as unresolved. Do not complete the graph using a guessed repository match.

### 4.3 Correlation and time semantics

Every node key includes tenant and source namespace. Examples: provider tenant plus principal object ID; cloud partition/account/region plus resource identifier; cluster UID plus workload UID; repository provider ID plus commit; registry/repository plus image digest.

Every edge includes relation, subject and object IDs, evidence IDs, source, event time, observed/collected time, validity interval, inference rule/version, confidence rationale, and limitations. Store observations immutably; build current views from them. Preserve conflicting evidence for investigation.

An edge is trustworthy only for its recorded scope and time. An old deployment and a new IAM grant must not be combined into a path that never existed. A model alias can route to different providers over time; model the alias and each observed resolution separately. Repeated requests, retries, batches, failovers, and asynchronous work require child events and trace links.

Represent heuristic joins as candidate links requiring corroboration. Do not merge principals because they have the same email, or workloads because they share an IP. Record merge/split history and allow correction without destroying original observations.

## 5. Signal collection and backend architecture

Retain the original modular FastAPI/Python backend, PostgreSQL, React/TypeScript, and Docker Compose foundations. Add modules rather than introducing a service mesh, Kafka, and a dedicated graph database immediately.

| Module | Responsibility | Why now / why not more infrastructure |
| --- | --- | --- |
| Connector workers | Enumerate resources and read approved event/config sources; checkpoint progress | Independent plugin contracts give breadth without a separate service per vendor |
| Normalization | Convert source records into typed observations with tenant and timestamps | Prevents vendor-specific fields leaking into every business rule |
| Entity resolution | Stable identifiers, candidate joins, evidence-backed links | Product-specific value; names and probabilistic entity matching are insufficient alone |
| Graph/query layer | Typed nodes/edges and bounded, time-aware traversal | PostgreSQL tables and indexes are adequate for initial bounded paths; revisit a graph database after benchmarks |
| Static discovery | Local Semgrep rules plus narrow parser/manifest adapters for supported languages | Start with explainable rules; do not claim universal whole-program call-graph recovery |
| Runtime ingestion | Mesh gateway events and OTLP traces; authenticated sender enrichment | Reuses ZeroShield's gateway integration while recording off-gateway visibility gaps |
| Supply-chain adapter | Trivy output, CycloneDX imports, artifact/provenance links | One primary scanner first; avoid duplicate findings from several tools without demonstrated benefit |
| Exposure analysis | Data classifications plus identities, tools, deployment and route context | An identity graph becomes useful only when it explains actual source access and data impact |
| Control planner | Supported enforcement actions, approvals, compensating actions, verification | A discovered relationship does not create permission to mutate its source |

Semgrep supports local YAML rule packs. Package approved rules locally instead of relying on network registry lookup during offline scanning. [Semgrep local rules](https://docs.semgrep.dev/running-rules).

### 5.1 Connector capability contract

Each connector version declares:

- Source family and supported API/platform versions.
- Supported asset and event types.
- Discovery scope: organization, account, project, repo, device, or source collection.
- Required read permissions; optional content permissions separately.
- Optional remediation actions and their separate write permissions.
- Pagination, rate limits, maximum historical window and expected event latency.
- Incremental cursor and deletion semantics.
- Offline import/export support and schema version.
- Supported metadata fields and redactions.
- Last successful enumeration, event watermark, snapshot completeness, exclusions, and error reason.

Example observation contract:

```json
{
  "schema_version": "1",
  "tenant_id": "tenant-example",
  "source_instance": "mesh-prod",
  "source_event_id": "event-example-041",
  "event_type": "ai.model.invocation",
  "event_time": "2026-09-24T09:00:00Z",
  "received_time": "2026-09-24T09:00:02Z",
  "actor": {"kind": "workload", "id": "support-assistant"},
  "delegated_user_id": "user-example-B",
  "workload_uid": "workload-example-7",
  "requested_model_alias": "support-default",
  "resolved_model_id": null,
  "trace_id": "trace-example-12",
  "outcome": "blocked_before_forward",
  "evidence_kind": "observed",
  "payload_content_collected": false,
  "limitations": ["provider model not resolved because request was blocked"]
}
```

The ingestion identity must bind the tenant server-side. A producer-supplied tenant ID, trace ID, username, or workload label is not trusted authorization evidence on its own. Unknown JSON fields are bounded and sanitized; secrets must not be retained in opaque raw blobs.

### 5.2 API contracts to add

- `GET /v1/estate/assets`: scoped filtering by kind, approval, lifecycle, evidence, owner, environment and coverage.
- `GET /v1/estate/assets/{id}/evidence`: provenance and source references subject to separate evidence permissions.
- `GET /v1/estate/paths`: bounded time-aware graph queries with missing-edge explanations.
- `GET /v1/estate/coverage`: connector, scope, freshness, exclusion and capability matrix.
- `GET /v1/estate/supply-chain/{artifact_id}`: software and AI component inventory for an exact artifact version.
- `POST /v1/estate/reviews`: owner assignment, approval/exception scope and expiry.
- `POST /v1/estate/remediation-plans`: dry-run planning only; applying a plan uses a separate authorized workflow.

All endpoints use tenant-scoped opaque IDs and pagination. Limit graph traversal depth, result size, query time and export size. Do not expose credentials, raw prompts, or sensitive code snippets in ordinary asset list APIs.

## 6. Supply chain: necessary distinctions

| Capability | What it answers | What it does not establish |
| --- | --- | --- |
| SCA | Which libraries/packages and known vulnerabilities/licenses appear in inspected artifacts | Whether a vulnerable function is executed or exploitable |
| SBOM | Versioned software component inventory, identifiers and dependency relationships | Completeness of proprietary SaaS internals or safety of code |
| SAST/static AI discovery | Supported source-code patterns and possible flows without running the application | That an apparent path was deployed or executed |
| IaC analysis | Risks in supported infrastructure configuration | That desired configuration matches the running environment |
| Secret detection | Suspected embedded credentials or unsafe references | Permission to test a discovered credential against a live service |
| AI/ML-BOM | Model artifacts, prompts, tools, embeddings, datasets, frameworks and provenance when available | Authenticity of unknown training data or hidden provider implementation |
| Runtime evidence | Which operation was observed with available identity/context | Every operation that could happen or everything outside instrumentation |

Use CycloneDX as the initial exchange format; select and pin a schema with the fields needed for the release. Its AI/ML-BOM capabilities provide a basis for model/dataset metadata. Unknown provider-internal components remain explicitly unavailable rather than fabricated. [CycloneDX AI/ML-BOM](https://cyclonedx.org/capabilities/mlbom/).

For AI-specific components, retain a model file digest when available, registry origin, model/version alias resolution, adapter and embedding versions, tokenizer metadata, prompt/template hash, agent configuration revision, MCP package/image digest, and tool-schema hash. Training-data lineage is included only when the customer or provider actually supplies it.

Never import or execute untrusted repository code to discover its behavior. Never load arbitrary pickle/model files or enable remote model code during inventory. Scanners run with bounded CPU, memory, file size, archive depth and time, without source-system write credentials. Treat scanner JSON, tool descriptions and repository text as untrusted input, not instructions.

## 7. Blast radius and control assurance

Display three different answers:

1. **Potential exposure:** resources reachable under evaluated permissions and known conditions.
2. **Observed access:** resources seen in supported audit/runtime events during a stated interval.
3. **Confirmed disclosure/action:** evidence that the specific protected content or operation crossed a relevant boundary.

An IAM allow is not a complete proof of effective permission if resource policies, explicit denies, organization controls, network conditions, row policies, session restrictions or source semantics are missing. Mark the missing conditions. Absence of observed use is not proof that access is unnecessary.

Risk findings should state the affected data classes, reachable actions, trust boundary, identities, production context, evidence age and any unknowns. Keep risk severity separate from confidence and coverage. A high-impact suspected path may warrant review but must not be displayed as a confirmed leak.

Guardrails require their own lifecycle: exists, configured, attached to a route, observed evaluated, and tested for specified controls. A configured guardrail that is bypassed by a fallback route is not effective coverage.

Example finding: a production agent can invoke an MCP export tool using a shared service principal; that principal can read sensitive support records under evaluated source conditions; the downstream model route permits external egress. The finding is a potential exposure unless relevant access/transmission evidence exists.

## 8. Air-gapped and connected modes

| Mode | Collectable evidence | Enforcement boundary |
| --- | --- | --- |
| Connected customer-hosted | Local sources plus approved cloud/IdP/SaaS APIs and event exports | Customer-controlled gateway, workload, source APIs and endpoint controls |
| Controlled-egress / semi-disconnected | Explicit outbound destinations or approved collectors; local processing | Approved routes only; still not a fully isolated enclave |
| Fully disconnected enclave | Internal repos, registries, devices, identity, workloads, models, MCP and imported evidence | Local controls; no real-time mutation of unreachable public-cloud/SaaS resources |
| Historical import | Signed, bounded snapshots with capture time and collection scope | Analysis only until revalidated against an authoritative reachable source |

Install the complete UI/API, graph, classifiers, scanners, policy engine, gateway, remediation controller, audit store, identity integration and artifact registry inside the enclave. External fonts, analytics, update checks, license callbacks, online package downloads and cloud model dependencies must be eliminated or explicitly disabled.

Offline bundles contain signed images, rule packs, source catalogs, scanner databases, schemas, ML artifacts where needed, trust roots, migrations and rollback metadata. Validate signatures, hashes, approved signer identity, compatibility, freshness and anti-rollback policy before activation. A signature proves provenance/integrity under the trust policy, not that the bundle is harmless.

Trivy documents network dependencies beyond the core vulnerability database, including Java data, checks, VEX and update/telemetry endpoints. Mirror required content and disable unwanted network behavior; test the exact pinned version with denied egress. [Trivy connectivity and air-gap requirements](https://trivy.dev/docs/latest/advanced/air-gap/).

Show database/rule age in the UI. “No vulnerabilities detected using database dated X” is acceptable; “up to date” is not if the enclave cannot know about newer advisories. Scanner offline success does not mean it detects future vulnerabilities.

## 9. Safe automated response

Discovery identifies candidate actions; it does not grant remediation authority. Start with observation and narrowly scoped containment. Require separate, customer-approved permissions for source changes.

| Finding | Initial action | Higher-authority action |
| --- | --- | --- |
| Unknown production model endpoint | Review and alert; block only if an explicit allowlist already governs that route | Approve endpoint or change deployment routing |
| MCP tool/schema drift | Suspend the affected governed binding under a preapproved policy | Review and approve a new schema/version |
| Stale vector ACL | Deny stale chunks on protected retrieval paths and schedule refresh | Repair supported source/index mappings after authoritative recheck |
| Vulnerable AI package | Attach finding to affected artifact/workloads; produce a fix proposal | Approved rebuild and canary deployment, not an arbitrary in-place production upgrade |
| Unsanctioned SaaS AI | Owner/approval workflow and scoped alert | Customer-approved IdP grant revocation or managed egress block |
| Sensitive source oversharing | Simulate affected identities and request approval | Supported source-native ACL correction with verification |

Cross-system changes are generally not one atomic database transaction. Use a durable saga: step journal, preconditions, idempotency keys, limited credentials, retries, reconciliation and compensating actions. A compensating action is a tested counter-action, not an assurance that every side effect is reversible.

Rollback must not automatically restore unsafe access. On failed repair, keep containment and escalate when reopening would re-expose data. Already transmitted data, emitted streaming tokens and third-party tool side effects cannot be “un-sent.”

The earlier no-model-receipt concept must be scoped: demonstrate that the instrumented, enforced request path did not forward a forbidden payload using gateway/model-spy evidence and bypass controls. An absence of cloud logs cannot prove global non-disclosure. For unattended agents, compare against explicit approved workload authority; for delegated actions, also require the human's applicable authorization. Never substitute a broad service account silently.

## 10. Frontend additions

These are design requirements, not changes already made to the published prototype.

| Screen | Main workflow | Required truthfulness states |
| --- | --- | --- |
| Estate Overview | AI assets by type, new discoveries, unowned/prohibited assets, scan/activity freshness | Unknown coverage visible beside totals; no invented enterprise-wide discovery percentage |
| AI Resources | Filter apps/agents/models/MCP/guardrails by environment, owner and approval | Installed/configured/active distinct; provider tenant and version visible |
| Supporting Resources | Inspect code, builds, workloads, devices, identities and data sources | Repository existence distinct from proven deployment |
| Code-to-Cloud Explorer | Follow a selected version to deployment, identity, model and data | Clickable edge evidence; candidate edges visually distinct; missing links explicit |
| Supply Chain | Inspect artifact SBOM, model/tool provenance and correlated vulnerabilities | Database age, parser coverage, affected artifact versions, reachability unknown |
| Shadow AI Review | Assign owner; approve, prohibit or grant an expiring exception | Approval scope by tenant, user/group, environment, feature and version |
| Coverage and Connectors | Connect sources, inspect permissions, lag, event categories and gaps | Read/write capabilities separate; partial enumeration not “healthy” |
| Remediation | Simulate, review plan, approve, execute and inspect verification | Dry-run/applied/verified/partial/contained/manual review distinctly labeled |

Extend the existing inventory and finding drawers with Sources, Versions, Identity, Data Access, Supply Chain, Activity and Evidence tabs. Keep a compact table as the default; graph visualization is for explaining selected paths, not rendering the entire enterprise at once. Every graph interaction needs an equivalent accessible table view.

## 11. Incremental release sequence

| Gate | Extension tasks | What works at this gate | Relationship to original plan |
| --- | --- | --- | --- |
| E0 Foundations | D01–D03 | Evidence contracts, replayable collection, scoped resolution | Extend original P0; do not wait until after T64 |
| E1 Local discovery MVP | D04, D06–D08, D16, D19 initial views | Local repo to actual Docker artifact/workload to observed model call, with basic SBOM and honest gaps | Build around P1/P2; preserve original posture and RAG gates |
| E2 Connected discovery | D05, D09, one of D10–D12 | One real repo provider, one real IdP, one real cloud, linked through the same graph | Extend P5 per-connector release gates |
| E3 Broader estate | Remaining D10–D12, D13–D15, D17 | Multi-cloud, managed endpoint, local/remote MCP and SaaS AI discovery | Incremental versions; unsupported sources remain explicit |
| E4 Data-aware controls | D18, D20, full D19 | Evidence-backed blast radius and supported closed-loop response | Integrate original P2–P4 and P6 safeguards |
| E5 Disconnected release | D21 | Cold offline install, local discovery and remediation, signed update/restore | Air-gap constraints designed from E0; certification requires P6 readiness |
| E6 Scale and harden | D22 | Measured bounds, fault recovery, isolation and connector certifications | Extend P7; benchmark the actual supported scope |

D16 can follow D04 without waiting for cloud integrations. D21 requirements constrain every earlier task even though full certification is later. Choose the first real cloud and IdP from a design customer's environment; AWS-first is a proposed engineering default, not a commitment to exclude Azure or Google.

## 12. Common reproducible verification protocol

Every D task includes the protocol below plus its specific checks. None of these commands exists merely because it is named here; create the targets and tests before marking the task complete.

1. Pin application, scanner, rule, browser, fixture and container versions/digests. Never depend on floating `latest` or online model output for golden assertions.
2. Use synthetic data and disposable scoped test environments. Never use real customer secrets as fixtures or issue destructive tests against production.
3. Bring up the real API, worker, PostgreSQL, Keycloak, web UI and applicable local source services using Docker Compose. Wait for health/readiness and prove real sign-in.
4. Seed positive and negative fixtures through documented interfaces. Replay fixture records through the actual collector/normalizer rather than injecting final UI JSON.
5. Run unit/property tests and live API/integration tests. Exercise pagination, permission denial, duplicate delivery, out-of-order events, restart, stale input and tenant mismatch.
6. Use Playwright against the live frontend/backend. UI component mocks do not complete a connector or product gate.
7. For external adapters, fixture replay certifies the parser only. Separately run a read-only live test in an authorized test tenant/account. Missing credentials mean live validation is blocked, not passed.
8. Save a sanitized evidence manifest with commit, digests, DB/rule versions, connector scopes, event windows, test commands, pass/fail counts, screenshots and known exclusions. Secret values and raw prompts are excluded.

Proposed commands:

```bash
make estate-up
make estate-seed SCENARIO=code-to-runtime
make estate-test TASK=D08
make estate-ui-test TASK=D08
make estate-evidence TASK=D08
make estate-test-all
make estate-airgap-test
```

Evidence path convention: `artifacts/estate/Dxx/<run-id>/`. The air-gap target runs in a disposable VM or controlled test network with actual host and container egress denied. A Compose internal network flag alone is not accepted as comprehensive air-gap proof.

## 13. Detailed implementation tasks

### D01 — Freeze the taxonomy and coverage contract

**Start/dependencies:** Original T01–T03 contracts; this addendum Sections 1–3. This is the first extension task.

**Implementation:** Define typed assets, observations, relationships, approval scopes and independent lifecycle/evidence/coverage fields. Add migrations and API schemas. Create fixtures for all six AI forms, including an installed-but-unused assistant and an opaque SaaS AI feature. Document supported vs planned capabilities and a classification rule version.

**Why / why not:** A consistent ontology enables shared analysis; a binary `is_ai` flag cannot distinguish an SDK, an active agent and an AI-capable SaaS product.

**Example:** A repository with an unused model SDK becomes a software dependency and AI candidate, not an active agent.

**Docker verification:** Load fixtures; validate schema compatibility and invalid state combinations; read back tenant-scoped assets. **Frontend:** Filters distinguish candidate, configured and active; missing evidence renders “unknown.”

**Pass:** All six forms have explicit representations and fixture expectations. **Fail:** Package-only or login-only evidence creates confirmed active AI. **Hard constraint:** Approval and activity are independent. **Retain:** Schema snapshot, migrations and truth-table test results.

### D02 — Build the collector and normalization contract

**Start/dependencies:** D01 and original authenticated worker/job infrastructure.

**Implementation:** Add connector capability manifests, typed event envelopes, credential references, cursor persistence, retries, idempotent delivery and bounded dead-letter handling. Separate complete snapshots from partial pages. Bind tenant to collector authentication, not request-body claims. Track event time, ingestion time and latest successful complete snapshot independently.

**Why / why not:** Incremental, replayable ingestion supports rate-limited APIs and offline imports. A cron script that replaces the entire inventory can erase resources after a transient failure.

**Example:** A five-page source listing fails on page four. Keep previous assets and mark the current snapshot partial.

**Docker verification:** Replay duplicates/out-of-order events; stop worker mid-page; inject 403/429/5xx and malformed records. **Frontend:** Show reason, scope, cursor progress and freshness without revealing secrets.

**Pass:** Resume loses no committed observations and creates no duplicate canonical assets. **Fail:** Partial enumeration retires unseen assets or advances past uncommitted events. **Hard constraint:** Read credentials cannot invoke writes. **Retain:** Replay manifest, restart transcript and coverage screenshots.

### D03 — Implement evidence-backed entity resolution

**Start/dependencies:** D01–D02.

**Implementation:** Build tenant/source-qualified keys, typed edges, time intervals and evidence references. Use exact provider IDs and artifact digests for strong links. Store weaker name/time/network correlations as candidates. Add merge/split audit and bounded traversal. Keep current and historical states distinct.

**Why / why not:** Cross-source linking creates the code-to-cloud story; indiscriminate fuzzy merging creates false attack paths.

**Example:** Two tenants have an identity named `assistant` and an image tag `prod`; they must never merge.

**Docker verification:** Exercise collisions, principal rename, deleted-and-recreated identities, conflicting digests, duplicate imports and non-overlapping edge intervals. **Frontend:** Edge drawer shows origin, time, reasoning and confidence; unresolved links remain visible.

**Pass:** Exact joins reproduce the fixture graph and uncertain joins remain candidates. **Fail:** A path mixes incompatible historical states or crosses tenants. **Hard constraint:** An inferred edge cannot authorize runtime access or trigger source writes. **Retain:** Golden graph, query tests and merge history.

### D04 — Discover AI in local code and configurations

**Start/dependencies:** D01–D03; a fixed synthetic repository corpus.

**Implementation:** Support Python and TypeScript patterns first. Inspect manifests/lockfiles, direct SDK calls, HTTP endpoints, model/framework configs, tool registration and agent loops. Add explicit LiteLLM/proxy alias and fallback-route parsing for supported versions. Store file/commit/rule location and distinguish test/example code. Use local rules, resource limits and no repository execution.

**Why / why not:** Static evidence locates possible AI behavior before deployment; arbitrary wrappers, dynamic imports and generated endpoints prevent universal resolution.

**Example:** A function calls a company wrapper that routes through LiteLLM. Link the statically supported wrapper; keep the final model unknown until routing/runtime evidence exists.

**Docker verification:** Scan positive, dead-code, comment-only, unused-dependency, dynamic-wrapper and malformed-file fixtures. **Frontend:** Explain why a candidate exists and which part is unresolved.

**Pass:** Golden-corpus positives and negatives match the documented support matrix. **Fail:** Merely containing the word “AI” or an SDK import marks active use. **Hard constraint:** No package install, import hooks or credential use. **Retain:** Detector version, corpus results and bounded-parser tests.

### D05 — Add GitHub and Azure Repos collection

**Start/dependencies:** D02–D04; authorized read-only test integrations.

**Implementation:** Implement repository enumeration, immutable commit retrieval, relevant config/lockfiles, CI metadata and incremental scan triggers for each provider. Treat cloud and self-hosted variants as separate certifications. Validate webhook authentication and replay protection; offer polling and signed offline Git exports. Match monorepo subprojects and their build contexts explicitly.

**Why / why not:** Repository providers supply ownership and revision context; one default-branch scan does not describe every deployed branch or artifact.

**Example:** The main branch no longer uses an external model, but production still runs an older commit. Retain the older linkage.

**Docker verification:** Replay pagination, rename, archived repo, restricted subproject and forged webhook fixtures. Run separate live tests against disposable provider repositories. **Frontend:** Show scanned commit, branches in scope, owner candidates and read permission gaps.

**Pass:** Both adapters preserve commit identity and scoped coverage. **Fail:** Read failure is treated as deletion or cloud replay is labeled live-certified. **Hard constraint:** No source modifications, PR creation or arbitrary CI execution. **Retain:** Sanitized live read evidence and per-provider capability reports.

### D06 — Link commits, CI builds and immutable artifacts

**Start/dependencies:** D03–D04; an approved fixture build pipeline.

**Implementation:** Import CI run IDs, source revision/build inputs, image or binary digests and provenance attestations. Verify subjects and approved builder identities. Keep unsigned labels as declarations. Model multiple images from one monorepo and multiple rebuilds of one commit. Support local signed provenance for disconnected CI.

**Why / why not:** Artifact digests identify the code package; image tags can move. Provenance must be verified, not merely present.

**Example:** `assistant:prod` is retagged from digest A to B. Historical runs continue pointing to A.

**Docker verification:** Build two harmless fixture images; ingest a valid, tampered, wrong-subject and untrusted-builder attestation. **Frontend:** Show exact commit/build/artifact and verification status.

**Pass:** A verified source-to-artifact link exists only for valid approved provenance. **Fail:** A self-asserted image label receives the same trust as verified provenance. **Hard constraint:** Verify from imported trust material offline when required; no hidden online dependency. **Retain:** Digests, attestation metadata and verifier outcomes.

### D07 — Discover actual deployments and workload identity bindings

**Start/dependencies:** D03 and D06; original local container environment.

**Implementation:** Start with approved local deployment snapshots and a constrained collector; then support Kubernetes inventory via read-only API credentials. Record actual running image digests, workload UIDs, namespaces, service accounts and deployment intervals. Add serverless/VM artifacts through cloud adapters. Treat local Docker-socket access as highly privileged and avoid granting an unrestricted socket to a network-facing service.

**Why / why not:** A deployment manifest describes intent; runtime inventory establishes which artifact is actually running.

**Example:** A failed rollout leaves A running although desired state names B. Show both.

**Docker verification:** Run both fixture revisions, stop one, replay partial/stale snapshots and test collector permission failures. **Frontend:** Compare desired/running state and current/historical workload instances.

**Pass:** Active instances link to their observed digest and scoped identity binding. **Fail:** Desired state overwrites actual running evidence. **Hard constraint:** Discovery cannot execute commands in customer containers or create privileged pods. **Retain:** Sanitized runtime snapshots and rollover tests.

### D08 — Correlate Mesh, proxy and runtime AI events

**Start/dependencies:** D02–D03, D07, original runtime gateway integration contracts.

**Implementation:** Normalize authenticated Mesh events and version-pinned OTLP mappings. Preserve workload identity, delegated user where verified, parent/child calls, proxy route revision, requested alias, actual provider/model when observed, attempt outcome and tool/retrieval spans. Add adapters for direct and proxied calls. Separate locally denied attempts from provider-accepted invocations.

**Why / why not:** Runtime resolves behavior static analysis cannot; a caller-provided trace ID is correlation data, not identity proof.

**Example:** One application request retries provider A and falls back to B. Show one logical request with both attempts, not three independent apps.

**Docker verification:** Use a real local app, proxy and deterministic model-spy endpoint; test direct/proxied calls, forged labels, missing IDs and sampling gaps. **Frontend:** Trace detail distinguishes requested and resolved models.

**Pass:** Supported calls link to the correct workload and attempt history. **Fail:** Sampled trace absence is treated as no activity or a claimed alias becomes a proven model version. **Hard constraint:** No raw prompt/response collection by default. **Retain:** Sanitized spans and spy receipts.

### D09 — Add identity and approval context

**Start/dependencies:** D02–D03; local Keycloak baseline and read-only test Entra/Workspace tenants when available.

**Implementation:** Import immutable users/groups/application IDs, service identities, supported grants and relevant activity categories. Maintain human and workload principals separately. Link owner candidates through trusted directory/repository metadata with confirmation. Add scoped approval records and expiring exceptions. Never infer identical identities from email alone.

**Why / why not:** IdPs reveal access relationships and ownership; they do not reveal every model request or capture personal-account usage outside their boundary.

**Example:** An approved SaaS application has a newly enabled AI feature with no approval. Mark the feature pending, not the entire employee malicious.

**Docker verification:** Replay group changes, service-principal sign-ins, guest users and duplicated display names; validate each external adapter live separately. **Frontend:** Human/workload filters and approval expiry behave correctly.

**Pass:** Scoped identity links and exceptions reconcile reproducibly. **Fail:** SSO login is presented as confirmed AI invocation. **Hard constraint:** Read integration cannot revoke grants. **Retain:** Identity test matrix and least-privilege capability evidence.

### D10 — Add AWS AI resource and activity discovery

**Start/dependencies:** D02–D03, D06–D08; customer-approved test account and regions.

**Implementation:** Inventory supported Bedrock agents, knowledge bases, guardrails and relevant model configurations; ingest operation-specific CloudTrail events and optional invocation metadata. Join workload/IAM, function/container and artifact records through authoritative identifiers. Add account/region event-category coverage checks and schema-version fixtures. Keep unsupported endpoints and conditional IAM semantics explicit.

**Why / why not:** AWS inventory plus audit provides configuration and activity context; generic IAM scanning or one event stream is incomplete.

**Example:** An agent exists, but its invocation data-event category was never enabled. Show configured resource with activity coverage missing.

**Docker verification:** Replay signed/sanitized event fixtures with duplicates, missing categories and role sessions. Separately perform a minimal approved live invocation and verify its actual event path. **Frontend:** Account/region/category matrix distinguishes absent events from disabled logging.

**Pass:** Supported test invocation, identity and workload correlate with evidence. **Fail:** All AWS AI is marked monitored after one successful API read. **Hard constraint:** Do not enable content logging, provision services or mutate IAM without separate approval. **Retain:** Operation matrix, read scope and live event reference.

### D11 — Add Azure and Foundry discovery

**Start/dependencies:** D02–D03, D08–D09; approved Azure test subscription/project.

**Implementation:** Read supported resources/deployments and agent configurations; collect managed-identity/application context and available diagnostic/Application Insights traces. Distinguish deployment names from underlying model versions. Map model/tool/retrieval events with per-feature support and preview status. Surface diagnostics permissions and configuration gaps separately from inventory failures.

**Why / why not:** Resource enumeration cannot replace agent execution tracing; traces can contain sensitive content and require minimization.

**Example:** Foundry resource discovery works while the telemetry store denies access. Inventory remains valid; runtime visibility is blocked.

**Docker verification:** Replay resource/trace fixtures, deployment renames, missing model versions and 403 responses. Validate one approved live project separately. **Frontend:** Show resource, deployment, identity, trace linkage and precise missing capability.

**Pass:** Supported resource and runtime evidence are independently accurate. **Fail:** A discovered resource becomes a confirmed active, fully guarded agent without trace evidence. **Hard constraint:** No automatic diagnostics/content capture or role assignment. **Retain:** Adapter schema, sanitized live trace and permission matrix.

### D12 — Add Google Cloud, Gemini API and Workspace adapters

**Start/dependencies:** D02–D03, D08–D09; separately authorized source scopes.

**Implementation:** Create separate modules for Google Cloud AI inventory/audit, Gemini API project evidence, and Gemini Workspace AI-specific events. Inventory current supported export/API capabilities instead of assuming UI-visible logs have an API. Maintain service-name/method mappings with versioned fixtures. Record Data Access configuration and content-logging policy. If automated export is unavailable, support an approved import and mark it accordingly.

**Why / why not:** These products share branding, not a uniform activity schema or permission model.

**Example:** A Workspace AI-feature event proves feature use; it does not identify the internal model weights or training data.

**Docker verification:** Replay one fixture per family, cross-project collisions and disabled logging; certify available live interfaces independently. **Frontend:** Distinct connector cards and coverage dates; do not aggregate them into one “Gemini connected” guarantee.

**Pass:** Each family has a truthful separately tested capability status. **Fail:** Workspace sign-in or Cloud logging implies Gemini API prompt visibility. **Hard constraint:** Never enable data-sharing, logging or dataset upload implicitly. **Retain:** Family-specific schema and live/import certification records.

### D13 — Discover managed coding agents and local models

**Start/dependencies:** D01–D03; approved endpoint collection surface or EDR integration.

**Implementation:** Define an OS/client-version support matrix. Read approved package/extension inventory and narrowly scoped AI client configuration. Ingest process start/parent metadata when authorized. Track installation, configuration, invocation evidence, local model endpoints and per-device/client bindings. Minimize process arguments; collect secret references, not environment dumps. Prefer existing EDR/MDM integrations before building a general endpoint agent.

**Why / why not:** Cloud/IdP signals miss local stdio tools and offline models; endpoint collection brings privacy and maintenance costs.

**Example:** A coding assistant and a local model are installed but not running. Report both as installed/configured, not active.

**Docker verification:** Test parser and ingestion using sanitized endpoint fixtures; Docker is not a substitute for native OS verification. **Frontend:** Device view shows collection scope and last seen. Run separate Windows/macOS/Linux live tests only for OSes declared supported.

**Pass:** Installation vs execution remains distinct. **Fail:** Unmanaged devices are implicitly included or one OS fixture certifies all OSes. **Hard constraint:** No covert monitoring, unrestricted home-directory scraping or collection of personal chat history. **Retain:** Native platform results and privacy-field allowlist.

### D14 — Discover MCP bindings, tools and guardrail drift

**Start/dependencies:** D02–D03, D08, D13 for endpoint-local discovery; original P4 controls for enforcement.

**Implementation:** Add versioned parsers for supported local/hosted client configurations and admin exports. Model server, client binding and tool versions separately. Read metadata only from approved endpoints; do not execute an unknown stdio command to enumerate it. For approved test servers, inspect tool schemas and authenticate appropriately. Monitor schema/config changes, downstream identity references and guardrail attachment/evaluation evidence.

**Why / why not:** An MCP process can be entirely local. HTTP authorization and stdio credential handling are different; do not apply one token model universally. [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).

**Example:** A familiar tool name changes to a new schema with export capability. Mark binding drift; retain both versions.

**Docker verification:** Run approved harmless stdio and HTTP fixtures; test rogue URLs, wrong token audience, schema drift and malformed manifests. **Frontend:** Show transport, client, offered vs invoked tools, schema and enforcement status.

**Pass:** Changes are detected without unsafe tool execution. **Fail:** “read-only” tool annotation is treated as proof of no side effects. **Hard constraint:** Server-advertised metadata is untrusted; SSRF and scope restrictions apply. **Retain:** Version diffs, auth negative tests and tool-call counters.

### D15 — Add embedded-SaaS AI visibility

**Start/dependencies:** D02–D03, D09; one approved SaaS with AI-specific administrator evidence.

**Implementation:** Build SaaS product/tenant/feature nodes; combine IdP access, feature settings, AI-specific audit records and dated vendor declarations. Add sanctioned/unsanctioned feature scope and an explicit vendor-internal visibility boundary. Managed browser/SSE metadata can provide supporting evidence, not universal content visibility. Record entitlement/API limitations.

**Why / why not:** Many applications contain optional AI; marking every SaaS login as AI use creates misleading inventory.

**Example:** Two employees use a CRM; only one emits an AI-summary feature event. Attribute observed AI use only to the supported event.

**Docker verification:** Replay login-only, feature-enabled, feature-used and opaque-vendor fixtures, plus a disconnected adapter. Test one real approved tenant separately. **Frontend:** Distinguish AI-capable, enabled, observed use and unknown internals.

**Pass:** Unsupported proprietary code/models/supply chains remain unknown. **Fail:** A vendor catalog assertion becomes proof of customer invocation. **Hard constraint:** No scraping employee conversations or vendor internals without an authorized interface. **Retain:** Evidence classification matrix and sanitized live proof.

### D16 — Add SCA and SBOM correlation

**Start/dependencies:** D04 and D06; scanner package/rule/database versions selected and reviewed.

**Implementation:** Integrate Trivy as the initial scanner behind a replaceable adapter. Analyze supported lockfiles and exported container artifacts; ingest CycloneDX BOMs. Normalize package identifiers, versions, locations, dependency relationships, vulnerability aliases, licenses and scan database age. Correlate by exact artifact digest. Keep installed component, declared dependency and vulnerability reachability distinct.

**Why / why not:** Reusing scanners accelerates commodity detection; the product's added value is linking findings to running AI, identities and data. Multiple scanners are deferred until measured incremental coverage justifies deduplication cost.

**Example:** Main branch has a patched package while production still runs the vulnerable artifact. Preserve the production finding.

**Docker verification:** Scan a frozen fixture artifact with a fixed advisory database, malformed SBOM and no-network conditions. **Frontend:** Show affected workloads and database date, with reachability unknown where untested.

**Pass:** Findings bind to the correct artifact and reproduce under pinned inputs. **Fail:** Latest source scan marks an older deployment patched. **Hard constraint:** No execution of scanned artifacts; review scanner/rule redistribution obligations. **Retain:** BOM, scanner manifest and digest-linked results.

### D17 — Extend the BOM to AI artifacts and configurations

**Start/dependencies:** D06, D14, D16; original RAG provenance model.

**Implementation:** Add model artifact/digest and provider alias nodes, embedding/tokenizer versions when available, prompt/template hashes, agent configuration versions, MCP package/image and schema hashes, dataset/index references and supplied provenance. Import/export supported CycloneDX fields and documented extensions. Never fabricate provider training-data lineage. Separate semantic prompt changes from software dependency changes.

**Why / why not:** Package SCA alone misses prompt/tool/model drift; a model digest alone does not establish its behavioral safety.

**Example:** A prompt template changes the agent's tool-use instructions while the container image stays the same. Record a new configuration version and affected runs. Instructions do not grant permissions; independently enforced tool authorization must still apply.

**Docker verification:** Use small non-executable model metadata fixtures; modify template/schema/hash and compare versioned BOMs. **Frontend:** Display known, unavailable and declared-only provenance distinctly.

**Pass:** AI configuration changes appear independently of container updates. **Fail:** Proprietary model internals are invented or model files are loaded to inspect them. **Hard constraint:** No arbitrary deserialization or remote model code. **Retain:** BOM schema validation and drift comparison evidence.

### D18 — Compute data-aware blast radius and control gaps

**Start/dependencies:** D03, D08–D09, D14, and original classification/source authorization/RAG tasks. Cloud adapters are optional per supported path.

**Implementation:** Join AI workload, identity, tools, source permissions, sensitivity, index provenance and egress routes. Add bounded time-aware path queries. Produce potential, observed and confirmed outcomes separately. Explain unresolved permission conditions. Track guardrail existence/attachment/evaluation and route bypass separately. Test read, write, delete and export as distinct actions.

**Why / why not:** Graph reachability alone does not equal effective access; a source authorization engine can impose conditions the graph has not captured.

**Example:** An agent can search permitted cases but its export tool uses broader service credentials. Flag that specific authority transition and sensitive data scope.

**Docker verification:** Reuse Alice/Bob RAG fixtures; add explicit deny, unknown row policy, stale group membership and alternate egress. **Frontend:** Show path evidence and unknown conditions without calling a potential path a breach.

**Pass:** Authorization outcomes match authoritative fixture tests; unresolved cases remain unknown. **Fail:** Missing conditions become allowed or every accessible row is labeled leaked. **Hard constraint:** A risk score never grants access. **Retain:** Path queries, source checks and negative-case evidence.

### D19 — Implement operator discovery and investigation workflows

**Start/dependencies:** D01–D03 and whichever adapters are ready; extend incrementally at each gate.

**Implementation:** Build the eight workflows in Section 10 using the existing UI patterns. Add server-side filtering/pagination, saved scope, evidence drawers, source freshness, owner assignment and approval history. Use bounded path visualization with a tabular equivalent. Restrict evidence and exports separately from basic inventory. Show data-plane enforcement status independently from connector health.

**Why / why not:** An attractive topology map without evidence is not an investigation tool; tables remain better for triage at scale.

**Example:** From a critical agent finding, open the exact image, source commit, tool binding, data path and remediation preview without losing scope.

**Docker verification:** Serve the actual web/API stack with seeded multi-tenant observations. **Frontend:** Run Playwright for filters, deep links, loading/empty/error/stale states, keyboard use, access denied, drawer navigation and sanitized export.

**Pass:** All visible links resolve to scoped evidence; screenshots agree with backend state. **Fail:** Mock-only data or hidden unknowns make coverage look complete. **Hard constraint:** Do not expose credentials, raw prompts or another tenant's resource names. **Retain:** Browser report and representative screenshots.

### D20 — Extend controlled remediation to estate findings

**Start/dependencies:** D18–D19 and original P4/P6 enforcement/remediation safeguards.

**Implementation:** Add action capabilities per connector; dry-run impact, explicit approval tiers, authoritative re-read, target-version preconditions and plan expiry. Use a durable per-step journal and idempotency keys. Start with one governed MCP binding suspension or stale-chunk containment, not broad IAM rewrites. Verify both denial and continued authorized operation. Use compensation only when it remains safe.

**Why / why not:** Multi-system repairs are not automatically atomic; a successful API response is not verified risk reduction.

**Example:** Suspend an unapproved export tool binding, retain search, then verify the denied export caused no call at the controlled test endpoint.

**Docker verification:** Crash after apply, retry duplicate jobs, change source version during approval, revoke write permissions and fail verification. **Frontend:** Show dry-run/applied/verified/contained/manual-review states and approval identity.

**Pass:** Idempotent containment and explicit verification succeed within scoped authority. **Fail:** Stale plans mutate newer config or compensation reopens unsafe access. **Hard constraint:** No LLM-generated arbitrary commands; no writes based solely on candidate graph links. **Retain:** Plan hash, step journal and before/after verification.

### D21 — Package and certify fully disconnected operation

**Start/dependencies:** E1 capabilities, selected enforcement workflow, original P6 packaging; requirements apply from D01 onward.

**Implementation:** Bundle all images, front-end assets, schema/rule/scanner databases, optional local models, trust material and offline entitlement. Support internal IdP, Git and registries. Verify signatures and compatibility on import; implement staged update/restore. Make imported historical cloud evidence read-only and visibly dated. Provide local support diagnostics with customer-controlled export.

**Why / why not:** “Scanner runs locally” is insufficient if login, UI fonts, licensing, telemetry, trust checks or vulnerability updates call outside the enclave.

**Example:** Install on a fresh disconnected VM from the release media, discover a local app, block a test MCP action and inspect evidence in the frontend.

**Docker verification:** Deny host/container external DNS and networking; run cold install, reboot, expired/stale bundle, tampered bundle and rollback scenarios. **Frontend:** Complete sign-in and all certified workflows with a fresh browser cache.

**Pass:** Supported local workflows work with zero unapproved outbound attempts; stale evidence remains labeled. **Fail:** Online assets or an external control plane are required. **Hard constraint:** No real-time claim or remote remediation for unreachable SaaS/cloud. **Retain:** Network capture, install manifest, update/restore evidence and screenshots.

### D22 — Validate scale, failure recovery and release claims

**Start/dependencies:** Selected E1–E5 scope verified; original P7 methodology.

**Implementation:** Publish a connector/version/mode certification matrix. Define load targets from pilot workload: assets, edges, event rate, connector scopes and graph query limits. Run queue backpressure, rate-limit, replay, retention, backup/restore and temporal-correlation tests. Measure p50/p95/p99 ingestion/query latency and resource use. Separate collector loss from genuine inactivity. Re-run isolation and control tests under load.

**Why / why not:** Scaling only throughput can invalidate freshness and access guarantees; a dashboard demo is not platform certification.

**Example:** Events arrive late during a restart while a deployment and its permissions change. The rebuilt timeline must not invent a historical exposure path.

**Docker verification:** Scale real processes against generated bounded fixtures; document host limits and run longer qualification on the intended deployment profile. **Frontend:** Large inventory paging, bounded graph queries and stale-state warnings remain usable.

**Pass:** Published performance and recovery targets hold for the stated scope with security tests passing. **Fail:** Event loss is hidden, isolation fails, or fixture-only adapters are advertised as live-certified. **Hard constraint:** No universal coverage or zero-leak claims. **Retain:** Benchmarks, soak results, restore drill and release exclusions.

## 14. Release-blocking acceptance scenarios

| Scenario | Required result |
| --- | --- |
| SDK present, never called | Dependency/candidate only; not confirmed active AI |
| LLM call behind a supported wrapper and proxy | Supported static chain recorded; actual downstream model established only by relevant runtime/routing evidence |
| Dynamic unknown wrapper | Unresolved candidate; no invented endpoint |
| Image tag moves | Historical workload remains bound to original digest |
| Same IP, multiple workloads | No identity join based on IP alone |
| Agent exists, invocation logging unavailable | Configured asset with runtime coverage gap |
| SaaS login without AI-feature event | Access evidence only; AI use unknown |
| Local stdio MCP server | Discovered through supported endpoint/config evidence, not an assumed network port |
| Tool schema changes under same name | Versioned drift and governed-binding review |
| Guardrail exists but fallback bypasses it | Control gap visible; not fully protected |
| Source ACL revoked, vectors stale | Protected retrieval denies or quarantines stale content; refresh tracked |
| Partial connector enumeration | No unsupported deletion/retirement inference |
| Tampered collector tenant or workload label | Reject or quarantine; never trusted for authorization |
| Cross-system remediation partially fails | Preserve safe containment, reconcile and surface manual review |
| Offline scanner database is old | Scan result states database date and freshness limitation |
| External cloud inaccessible from enclave | Imported historical evidence only; no live/remediated claim |
| Customer admin controls unmanaged bypass path | Coverage exclusion and required deployment control documented |

## 15. Hard constraints

1. No claim to discover every arbitrary program, personal device or vendor-internal AI system.
2. No inference that an SDK, domain visit, SSO login or cloud resource proves active model use.
3. No secret extraction, live credential testing or execution of untrusted code as part of discovery.
4. No automatic new logging, data sharing, tenant role changes or source writes during read-only onboarding.
5. No raw prompt, response, token, environment or full source-code retention by default.
6. No merging identities across tenant/source boundaries using names, emails or IP alone.
7. No implicit allow from missing, stale or conflicting authorization evidence on protected paths.
8. No graph edge without provenance, time semantics and declared evidence strength.
9. No source-system mutation from an inferred path or a free-form LLM recommendation.
10. No all-or-nothing atomicity or reversibility claim for arbitrary distributed remediation.
11. No restoring known-unsafe permissions simply to satisfy a rollback routine.
12. No globally exact blast-radius claim when permission conditions or inventory scopes are missing.
13. No “fully air-gapped” claim while an external control plane or runtime dependency is required.
14. No “tests passed” claim based on a task specification, mock UI or fixture replay alone.

## 16. Initial connector onboarding order

First local demonstration: local Git fixture, local OCI artifact, constrained Docker inventory, Keycloak, Mesh/model-spy, PostgreSQL/pgvector and approved MCP fixtures. This needs no customer cloud credentials.

First connected customer pilot: select one repository provider, one IdP and one cloud aligned to that customer, then add a managed endpoint source if coding-agent coverage is required. Read-only permissions first; remediation authority is a separate onboarding decision.

Full scope: GitHub and Azure Repos; Entra and Google Workspace; AWS, Azure and Google Cloud AI; Gemini API and Workspace-specific activity; managed endpoint/EDR; approved SaaS AI integrations; MCP; build systems/registries; source data connectors already in the DSPM plan.

Customers authenticate these product integrations in their environment through supported read-only app/service identities. Connecting an app in this chat is not equivalent to deploying a production connector or granting enterprise-wide security visibility. Never paste production credentials into a plan or chat. Exact permissions must be generated and verified per connector version and selected scope.

## 17. Vocabulary

| Term | Meaning in this product |
| --- | --- |
| AI estate | The supported AI systems and their code, infrastructure, identities, data and controls within a declared organizational scope |
| Shadow AI | AI usage/configuration outside an applicable approval process; not simply any newly discovered asset |
| IdP | Identity provider, such as Entra, Workspace or a local identity service |
| Principal | A human or workload identity evaluated for an action |
| Workload identity | Identity assigned to running software rather than a person |
| Delegated identity | Human authority explicitly carried into an action performed by software |
| MCP | Protocol through which clients interact with tool/resource-providing servers; transport and downstream authority still matter |
| stdio | Local process communication using standard input/output, not a remotely observable HTTP connection |
| AST | Structured representation of source syntax, useful for locating calls without executing code |
| SCA | Dependency/component analysis for vulnerabilities and related software risks |
| SAST | Static source analysis; related to but not the same as SCA |
| SBOM | Software bill of materials for a specific version/artifact |
| AI/ML-BOM | Model, dataset and AI-configuration provenance added to component inventory where available |
| Artifact digest | Content identifier used to distinguish immutable build outputs |
| Attestation | A signed statement about an artifact or process; its subject and signer must be verified |
| Provenance | Evidence of origin and transformations, not a blanket safety guarantee |
| Guardrail | A policy/control applied at a specific AI interaction boundary |
| Blast radius | Potential or observed consequences within stated identity, permission, data and time assumptions |
| ACL | Access control list or source-specific permission representation |
| RAG | Retrieval-augmented generation: retrieving eligible context for a model request |
| Vector chunk | A source-content fragment indexed for retrieval, with provenance and authorization metadata |
| OTLP | OpenTelemetry protocol used to transport telemetry to a collector |
| Evidence watermark | The latest point the collector can reliably claim to have processed, with source-specific completeness semantics |
| Idempotency | Repeating an operation does not produce unintended duplicate effects |
| Saga | Durable multi-step workflow with recovery/compensation rather than a universal atomic transaction |
| Air gap | Deployment boundary without live external connectivity; local dependencies must be self-contained |

## 18. Completion definition

The expanded product is ready for a supported release when an operator can discover a scoped AI asset, trace supported source/build/deployment/identity/model/data relationships, inspect supply-chain context, see every important coverage gap, and apply only authorized tested controls with auditable results. Completeness is asserted per connector and workflow, never for the unknowable entirety of an organization.

The first engineering deliverable remains small: D01 followed by D02 and D03, then a local code-to-runtime slice. Establish a correct shared graph before adding every provider. Preserve all original isolation, authorization, privacy and reproducibility gates.
