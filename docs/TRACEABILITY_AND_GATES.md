# Requirements traceability, verification gates and handoff record

This file connects the task families. It does not mark a capability implemented. Read the detailed task card named in each row before coding. `T` = core engineering tasks, `D` = shadow AI/code-to-cloud discovery, `L` = AI/DSPM lifecycle, `F` = frontend implementation and `N` = non-human identity extension. The master lifecycle file contains the full AI stage A01–A14, DSPM cycle C01–C08 and risk R01–R60 definitions.

## Nine product questions

| Question | First supported proof | Later expansion | Negative/unknown case |
| --- | --- | --- | --- |
| Q1 What sensitive data can this AI agent access? | T19–T26 source permission/path for an app; D18 blast radius | T35–T42 agents, D14 tools, L19 | No trusted identity or ACL → unknown/deny on protected retrieval |
| Q2 Which RAG/vector stores contain regulated data? | T19–T26 pgvector payload with source provenance | T46 Qdrant, L11 index lineage | Embedding without payload/source mapping → unknown |
| Q3 Which employees send data to AI services? | T27–T34 managed request path | T49 managed employee telemetry, D09/D15 identity/SaaS | Domain visit or inaccessible SaaS backend is not prompt evidence |
| Q4 Which agents have excessive permissions? | T35–T42 agent/tool principal inventory | D18 context graph, L19 | Unused permission alone is a review signal, not proof of excess |
| Q5 What enters a model prompt? | T28/T29 inspected managed adapter | D08 gateway signals, L17/L18 batch/provider paths | Bypassed or unobserved path is out of coverage |
| Q6 What leaves in model output? | T30/T31 inspected managed response | L17/L18 streaming/batch | Bytes sent before a decision cannot be recalled |
| Q7 Which MCP tools reach confidential data? | T36–T39 typed tool/resource decisions | D14 discovered bindings, D18 graph | Tool description is untrusted; downstream scope unverified |
| Q8 Can an agent read what the human cannot? | T22–T26 per-user retrieval check | T37–T41 delegated tool authorization | Missing/stale principal or ACL → deny on protected path |
| Q9 Can it automatically redact/block/mask? | T27–T34 controlled model path | T51, D20, L25 source remediation | P1 read-only discovery has no block claim |

The N01–N09 / F13–F17 extension in `NHI_SPIFFE_FRONTEND_AND_BACKEND.md` strengthens Q1, Q4, Q7 and Q8 by distinguishing workload identity proof from delegated user context, tool grants, source ACLs and an actual authorization decision.

For every answer expose the source, principal, data version, policy version, evidence kind, observed time and coverage limitation where applicable. A graph edge alone is not proof of allowed access.

## Shadow AI signal coverage

| Surface | Required signal classes | First task group | What cannot be inferred from one signal |
| --- | --- | --- | --- |
| Coding agents | Approved endpoint/extension config, managed endpoint logs, gateway events, identity | D04/D08/D09/D13 | A repository import does not prove use on a device |
| Desktop MCP | Managed config, server metadata, identity/token scope, execution audit | D13/D14/T35–T42 | Installed server does not prove a particular data read |
| Direct/framework LLM calls | Code/config references and observed network/model request | D04–D08 | A dependency or framework import is not runtime activity |
| Agentic code | Deployed artifact, principal, tools, model, data path and observed actions | D06–D08/D14/D18 | A static framework pattern does not prove exact blast radius |
| AWS/Azure/GCP managed AI | Service inventory, activity logs, IAM and resource versions | D10–D12, T43/T44 | Cloud service presence does not prove content or effective access |
| Embedded SaaS AI | IdP, admin settings, vendor declarations, available audit logs | D09/D15/T49 | Vendor internals absent from logs stay unknown |
| Supply chain | Dependency/SBOM, model/dataset/adapter provenance, build attestation | D16/D17/L05/L09/L15 | An SBOM alone does not prove runtime deployment |

The three views are AI resources, supporting resources and SCA/supply chain. Correlate them through a versioned graph: repository/commit → CI build → immutable artifact → runtime deployment → workload identity → model/tool → source data. For each edge record origin, timestamp, confidence, resolver and contradiction/unknown state. Never merge two identities merely because display names match.

## Lifecycle and DSPM stage gates

| AI stage | DSPM loop to apply | Task families | Representative risk and mandatory test |
| --- | --- | --- | --- |
| Purpose and acquisition A01–A02 | Discover/classify/assess | L01/L02/L05, T09–T13 | Unapproved data-use purpose cannot become an approved training input |
| Discovery and preparation A03–A04 | Discover/classify/lineage | T10–T15, L03/L04/L06/L07 | Derived/temporary copy inherits sensitivity; unsupported formats counted |
| Model selection/training A05–A06 | Assess/enforce/verify | L05/L08–L10, D16/D17 | Unknown provider retention and unapproved training source block managed promotion |
| RAG/agents A07 | Map access/enforce/verify | T19–T26, T35–T42, L11/L12 | Bob's forbidden source bytes never reach model fixture or tool result |
| Evaluation/release A08–A09 | Assess/verify/monitor | L13–L16 | Approval binds exact dataset/model/code/prompt/policy versions |
| Inference and actions A10 | Enforce/verify/monitor | T27–T42, L17–L19 | Managed path bypass, output streaming and tool side effect are tested |
| Monitor/change A11–A12 | Monitor/assess/remediate/verify | L20–L25, T51/T52 | Revocation, drift and stale approvals require reassessment |
| Retirement/disposal A13–A14 | Remediate/verify/rediscover | L26–L29, T54 | Backup restore cannot silently resurrect forbidden managed copies |

At each supported stage run the DSPM cycle C01 discovery → C02 classification → C03 lineage/access → C04 assessment → C05 scoped control → C06 independent verification → C07 monitoring → C08 lifecycle change/retirement. Some stages have no safe automatic control; record a review action and limitation instead of pretending enforcement.

## Controlled remediation contract

The automatic action engine starts only after a supported source integration exists. Detection identity stays read-only. A separate writer identity gets a narrowly scoped permission set for one action type, source and tenant. The workflow is:

1. **Propose** action with finding ID, evidence/version, expected source state, target, scope and impact.
2. **Preview** affected assets and legitimate paths; block on stale evidence, missing capability, wrong tenant or unknown rollback.
3. **Authorize** under policy with bounded approval for consequential actions. A human may be required; low-risk actions can be preauthorized by a customer-owned policy.
4. **Execute** idempotently with a unique action key, expected version/ETag, timeout, retry bound and audit trail.
5. **Read back** actual source state through the connector, then re-test the original unauthorized path and one expected legitimate path.
6. **Close or compensate** only on verified result; otherwise preserve partial state and escalate. Never equate an accepted API request, queued job or UI disappearance with a resolved finding.

Air-gapped mode runs the same engine inside the enclave with local package/image/model/signature manifests, no outbound dependency and customer-managed update import. Remediation can only affect reachable systems with provisioned local credentials. Test egress denial during both normal and failure paths. Clearly report unreachable source or unavailable dependency as `Blocked`/`Unknown`.

## Gate matrix

| Gate | Required live evidence | Required negative evidence | Release blocked by |
| --- | --- | --- | --- |
| Foundations T08 | Fresh Compose boot, DB/API/browser round trip, OIDC and restricted-role RLS | Wrong tenant, wrong audience, DB outage, canary leakage | Static-only UI, skipped check, missing Docker image, cross-tenant path |
| Posture T18 | Source → scan → inventory → classification/finding → rescan | Unsupported/partial scan, write denial, worker restart | Unknown coverage reported clean, duplicate finding or raw evidence leak |
| Protected RAG T26 | Alice allowed with source provenance; Bob denied before model input | Unknown ACL, stale/revoked ACL, source outage, cache replay | Forbidden bytes in retrieved/model-facing path |
| Runtime T34 | Managed request/output decisions with policy revision | Streaming interruption, adapter/provider failure, route bypass | Claimed block without enforced route, raw secret retained |
| Agent/MCP T42 | Principal/tool/argument decisions and audit | Wrong audience, changed metadata, side effect without approval | Tool description trusted as privilege or delegated identity lost |
| Workload identity N09/F13–F17 | SPIFFE issuer/bundle metadata, workload-to-agent binding, delegated subject, source policy and one traced live decision | Expired/wrong-audience SVID, stale foreign bundle, missing delegation, stale ACL, issuer outage and offline egress deny | Verified identity used as an implicit permission; synthetic UI mistaken for enforcement; credentials leaked to UI/logs |
| Connectors T50/D19 | Per-connector discovered assets and evidence-backed graph | Missing permissions, partial logs, conflicting links | Unsupported service advertised as fully mapped |
| Pilot T56/L31 | Previewed remediation, source readback, restore and air-gap rehearsal | Failed action, stale revision, unreachable source, egress deny | False closure or inability to recover |
| Release T64/L32 | Load/soak/security and upgrade/recovery on declared scope | Failure under concurrency, backup restore, tenant crossover | Unmeasured scalability or unsupported compliance claim |

## Per-task handoff record

Copy this template into a PR description or `artifacts/<task>/<run-id>/review.md`. Do not commit credentials, customer content or raw browser videos.

```text
Task ID / title:
Status: Planned | In progress | Verified | Blocked
Commit / branch / reviewer:
Supported and explicitly unsupported behavior:
Prerequisites proved (run IDs):
Code, OpenAPI, migration, generated-client, UI and documentation changes:
Fixture seed / version:
Runtime: OS/arch; Python/Node; DB/IdP; image digests; lockfile hashes:
Run ID / exact commands / test counts / required skips:
Live happy path evidence (DB + API + browser + logs as relevant):
Negative/failure/restart/concurrency evidence:
Security boundary evidence (tenant, identity, secrets, source write, egress):
Sanitized evidence paths + SHA-256:
Expected result / actual result / unresolved discrepancy:
Rollback or compensating action:
Next task and known blocker:
```

Never promote a task to `Verified` if a required browser flow was mocked, a database test used a privileged role, a scanner observed only a subset but reported full coverage, or a negative test did not actually exercise the forbidden path.
