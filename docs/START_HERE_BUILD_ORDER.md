# Start here: build order and current status

**Baseline reviewed:** `main` at `e76e485594736ffa76f2493a09ec2e76b842be40`, 2026-09-29. Update this section when code changes.

## 1. Product outcome

An operator should be able to identify an AI application, its supporting code/cloud/identity/model/tool resources, the sensitive source data and derived copies it can reach, the evidence quality and freshness of each link, the resulting risks, and whether a supported policy can prevent or remediate a particular data path. Customer data, credentials, prompts, embeddings, finding values and sensitive evidence stay within the customer boundary by default. A disconnected installation must be able to run all advertised local capabilities without an external control plane.

The product cannot infer facts from absent logs. Represent `declared`, `observed`, and `verified` evidence separately. Represent missing evidence as `unknown`; never silently turn unknown into allowed access or clean scan coverage. Read-only detection must never be described as runtime protection.

## 2. What exists now

| Area | Observed at baseline | Honest status |
| --- | --- | --- |
| Product contract | `docs/scope.json`, MVP capability notes, 19 OpenAPI operations, database reference SQL | Draft/structurally validated; no live API proof |
| Monorepo | Python workspace, React/Vite web package, lockfiles | Scaffold |
| API and workers | Package metadata and `__init__.py` only | No serving API or jobs |
| Browser UI | One static operator-console stub | No live API integration |
| Docker Compose | PostgreSQL, API, web, Keycloak service definitions | API/web Dockerfiles absent; not bootable as committed |
| Verification | Six harness tests passed locally; contract structural check passed | No live DB, IdP, browser or air-gap gate |
| Static checks | Ruff found 16 issues; mypy lacks typed package marker | Not green |

The current Compose health check calls `/health/live`, while the OpenAPI contract uses `/livez`; resolve that route contract before the first live gate. The verification runner must also stop excluding unimplemented foundation checks from a phase pass.

## 3. First work item

Start with **T02 and T03 repair**, using `FOUNDATIONS_T02_T08_TASKS.md`. T01 has written scope but is not a product implementation. Fix lock/toolchain execution, lint/typecheck, verification run identity and gate semantics. Then implement T04 as the first live vertical slice. Do not start an AWS connector, RAG, or a polished dashboard before T04 has a real database/API/browser round trip.

## 4. Release sequence

| Gate | Implement | Minimum customer-visible outcome | Must be proven before claiming the gate |
| --- | --- | --- | --- |
| G0 foundations | T01–T08; F01–F02 | Live System screen, persisted installation identity, authentication and tenant boundary | Clean Docker boot; outage/restart; restricted DB role; real IdP sessions; canary leak checks |
| P1 read-only posture | T09–T18; F03–F06 | Fixture source → durable scan → assets → masked classifications/findings → declared AI linkage | End-to-end browser flow; partial/unsupported coverage; rescan idempotence; no source writes |
| P2 protected RAG | T19–T26; F07 | User-aware retrieval for one real pgvector source | Alice allowed, Bob denied before model input; unknown ACL fail-closed; revocation and source outage |
| P3 runtime | T27–T34; F08 | Supported prompt/output policy with bounded adapter enforcement | Forbidden bytes absent across the enforced model boundary; streaming/failure/bypass cases |
| P4 agent/MCP | T35–T42; D13–D14; F09 | Agent and tool inventory, delegated decisions and scoped action control | Wrong user/tool/argument denied; changed server metadata and unsafe side effects tested |
| P4 identity extension | N01–N09; F13–F17 | Workload identity inventory, SPIFFE trust evidence and policy decision trace | Valid SVID does not imply data access; wrong audience, stale bundle, missing delegation and revoked ACL fail safely |
| P5 estate connectors | T43–T50; D01–D19; F10 | Code → build → deployment → identity → model/tool → sensitive data graph | Per-connector evidence and unknown coverage; no invented effective IAM access |
| P6 lifecycle and response | T51–T56; L01–L31; D20–D21; F11 | Purpose/data lineage, training/evaluation/release/retirement controls; previewed remediation | Version-bound policies; separate writer identity; readback and path retest; disconnected rehearsal |
| P7 scale and release | T57–T64; L32; D22; F12 | Supported customer release with measured operating limits | Load/soak, tenant isolation under concurrency, backup/restore and upgrade/rollback evidence |

The D and L task families extend the core T sequence. They do not mandate completing every optional cloud connector before a limited, accurately labeled release. For example, a fixture-only P1 release can be real even if Microsoft 365 is unknown and marked unsupported.

## 5. Architecture boundaries

Use Python 3.12, FastAPI, Pydantic, SQLAlchemy/Alembic, PostgreSQL, uv, TypeScript/React/Vite and Docker Compose as the initial modular monolith. Separate domain decisions from FastAPI routes and connector adapters. This makes an on-prem or air-gapped deployment viable and avoids binding business rules to a single cloud provider. PostgreSQL is the system of record; a graph projection may be added when measured queries justify it. Keep the graph model in relational tables first. A queue, Kubernetes, vector database in the catalog, hosted LLM or microservice split is a later decision supported by a workload or feature requirement.

Use Keycloak in development for a real OIDC authorization-code/PKCE flow. In customer deployments, accept a configured OIDC provider with issuer/audience checks and server-derived tenant membership. A browser-provided tenant header, opaque UI role, API key or model output is not authorization evidence. Scanner credentials must be read-only. Automated remediation must use a separate, narrowly scoped identity and transaction record.

## 6. Change and handoff rules

1. Choose one task ID and record prerequisites, supported scope, expected evidence and explicit negative tests in the PR.
2. Implement behind an interface with a live fixture and a known failure mode. Update OpenAPI, migration, generated client and capability matrix together when the contract changes.
3. Run the named task check on disposable test resources and collect a unique run ID, commit SHA, dependency/image digests and sanitized evidence.
4. Test the API/database boundary before the browser gate, then run the browser workflow against the same live stack with no mocks for required APIs.
5. Mark `Verified` only after success and failure assertions pass. Record blocked dependencies as `Blocked` with the exact reason.

## 7. Documents and single sources of truth

- Engineering detail and glossary: `AI_DSPM_Implementation_Plan_and_Tasks.md`.
- Shadow AI signal types, code-to-cloud, SCA: `AI_DSPM_Shadow_AI_Code_to_Cloud_Addendum.md`.
- AI lifecycle A01–A14, DSPM cycle C01–C08 and lifecycle tasks: `AI_DSPM_End_to_End_Master_Scope_and_Lifecycle_Tasks.md`.
- Concrete current foundation tickets: `FOUNDATIONS_T02_T08_TASKS.md`.
- UI sequence: `FRONTEND_PRODUCT_TASKS.md`.
- Exact first HTTP and data contracts: repository-root `openapi.yaml`, `API_GUIDE.md`, `DB_GUIDE.md`, `schema.postgres.sql`.
- Traceability and evidence: `TRACEABILITY_AND_GATES.md`.
- NHI/SPIFFE screens, proposed backend extension and test gates: `NHI_SPIFFE_FRONTEND_AND_BACKEND.md`.
