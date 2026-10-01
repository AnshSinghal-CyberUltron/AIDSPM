# Non-human identity, SPIFFE and agent authorization

**Status:** Product design and proposed backend contract. The connected Lovable screens are synthetic and do not authenticate a workload, validate an SVID, operate SPIRE/Vault, or enforce a production policy. This document extends T22–T26, T35–T42, D07/D09/D13–D14/D18, L19–L20 and F13–F17. It does not replace those task gates.

## 1. Why this belongs in AI-DSPM

An agent may run as a process or service that can call a model, retrieve a document, use an MCP tool or modify a source. To assess its data blast radius, the product needs the identity of the **running workload**, the human on whose behalf it acts (if any), the deployment and tool bindings, policy grants, source permissions and observed requests. Code declarations and a service-account name alone cannot prove that chain. Short-lived, verifiable workload identity can make the first link stronger, while data authorization remains a separate decision.

### Terms and limits

| Term | Meaning in this product | Why it matters / what it does not prove |
| --- | --- | --- |
| Non-human identity (NHI) | Identity associated with a workload, service, job or process | Separate it from a person and from a logical AI-agent record |
| SPIFFE ID | Structured identity name such as `spiffe://prod.example/agents/support`, within a trust domain | Names a workload; it does not itself grant permissions, encode capabilities or identify the delegated human |
| SVID | Verifiable document presenting a SPIFFE ID, commonly X.509 or JWT | Validate against the appropriate trust bundle, time and audience as relevant; do not display or store raw private key/token |
| X.509-SVID | Certificate-based identity, often used for workload mTLS | Check certificate chain, trust-domain bundle, SPIFFE SAN and validity; mTLS authenticates peers but does not decide access to payroll |
| JWT-SVID | Token-based identity for an intended audience | Check signature, exact intended audience, issuer/trust domain and expiry; bearer-token replay is a separate risk |
| Trust domain | Administrative identity namespace and its issuing keys | Distinguishes issuers and namespaces; matching name without the correct bundle is insufficient |
| Federation | Explicit exchange/validation of foreign trust bundles | Allows cross-domain identity verification; never an implicit grant to resources |
| SPIRE | A SPIFFE implementation that attests nodes/workloads and issues SVIDs | A configured registration/attestation result has evidence and freshness; a static ID in config is only declared |
| Attestation | Evidence that a particular process/node satisfied selectors or another issuer's conditions | Does not prove the AI tool's business purpose, delegated authority or allowed data |
| Human delegation | Bound user identity, session, purpose and expiry for an agent acting on behalf of a person | A workload SVID must not silently replace the user's source authorization |
| Authorization decision | Policy + source ACL + context + freshness evaluation for action/resource | Possible outcomes: allow, deny, unknown. Authenticated is not automatically authorized |

The console must label **declared**, **observed** and **verified** evidence; distinguish unsupported/no signal from a valid denial. In protected retrieval and sensitive actions, missing trusted identity, stale ACL, unknown bundle or absent user delegation must not become an allow.

## 2. Frontend screens

All screens use the existing ZeroShield navigation, design tokens, live-state vocabulary and responsive shell. Every sample count, timestamp and action is visibly marked as synthetic. No browser-only simulation is an enforcement claim.

| Screen | Route in Lovable design | Primary questions |
| --- | --- | --- |
| Identity inventory | `/identities` | What human, workload and logical agent identities are known; from which source; with what evidence and freshness? |
| Identity detail | `/identities/$id` | Which workload/deployment/agent owns this SPIFFE ID; what SVID metadata, attestation, delegation, grants, tool/data path and audit events are recorded? |
| Trust domains | `/trust-domains` | Which local/foreign bundles are available and fresh; where is federation explicitly configured; which links are unknown? |
| Decision lab | `/access-decisions` | Does a specific principal, delegated user, action and resource pass identity validation **and** policy/source authorization? |

### F13 — Inventory and navigation

**Start:** existing `src/routes/identities.index.tsx`, app shell and access-graph links. Add human/workload/agent filters; owner, provider/issuer, trust domain, credential state, last observed, evidence kind and coverage fields. Agents and workloads may link to each other but must be different entities. A row opens the detail route; no click-only inaccessible table row.

**Verify:** filter/search combination, empty result, keyboard/Enter navigation, back/forward, refresh, 320–3840 px, 200% zoom. **Pass:** a workload with no verifiable credential is `unknown` rather than healthy. **Fail:** an IdP sign-in is presented as proof of an agent tool call.

### F14 — Workload identity detail

**Start:** new `src/routes/identities.$id.tsx` and a synthetic fixture shared with inventory. Include SPIFFE ID, trust domain, SVID type, issuer, nonsecret fingerprint/reference, issue/expiry, validation result, attestation source, deployment/agent binding, human delegation, scoped grants, tool/data paths, evidence timestamps and credential lifecycle events. Model a healthy X.509 case, a JWT wrong-audience case, an expired/stale case, and an unknown local coding-agent case. Distinguish verification of identity from permission to act.

**Verify:** direct URL and invalid ID; chronological issue/rotate/expire events; wrong audience and expired state cannot display `authorized`; links to AI resource/MCP/graph work. **Fail:** raw certificate/key/JWT in HTML, URL, local storage or export.

### F15 — Trust domains and federation

**Start:** a trust-domain inventory with explicit bundle source/digest/freshness, foreign-domain relationship, observed refresh and gaps. A compact graph may supplement a table; the table must carry the information on mobile and for assistive technology. Do not infer federation from matching domain names.

**Verify:** local/foreign filters, stale/missing bundle, disconnected mode, keyboard focus and narrow-screen overflow. **Pass:** bundle refresh failure is visible and the related decision becomes unknown/deny. **Fail:** federation tile shows allowed resource access based on identity trust alone.

### F16 — Decision simulation

**Start:** select a fixture workload, optional delegated human, action, tool/source and environment. Trace checks in order: SVID/trust domain/audience/time → workload-to-agent binding → user delegation → policy permission/conditions → source ACL and freshness → final allow/deny/unknown. Show policy revision and evidence IDs. Inputs update the trace and result without side effects.

**Verify:** healthy scoped read allow; JWT audience mismatch deny; stale bundle unknown/deny; Bob accessing restricted payroll deny; missing delegation produces unknown and must be blocked by enforcement; action outside grant deny; a separately granted support KB read with stale source ACL reaches the last check and returns unknown; invalid selection reset. Compare displayed reason with independently specified fixture expectations. **Fail:** `credential valid` becomes `allow` without policy/ACL evaluation, the stale ACL branch is unreachable in fixtures, or `unknown` is treated as an executable allow.

### F17 — Cross-product investigation

**Start:** sidebar, command search, AI-resource detail, MCP server/tool, access graph and finding views. Add contextual links to the relevant identity and decision trace; a graph edge records the relationship and evidence, not authorization. Preserve mobile menu, dark/light theme, reduced motion and existing landing/console pages.

**Verify:** navigate from agent → workload identity → trust domain → decision → sensitive source and back; no broken routes or fabricated live integration state. Browser test with keyboard, reduced motion, 320/390/768/1440/3840 px, no critical console errors. **Pass:** same fixture IDs and status across pages. **Fail:** contradictory status between inventory, graph and decision trace.

## 3. Backend model and ownership (proposed)

Implement after T05/T06 isolation and identity foundations. Use PostgreSQL as source of truth with tenant-aware IDs/FKs, RLS under restricted runtime roles and immutable/audited event history. Reference the existing graph entity model rather than creating a second inconsistent identity store.

| Record | Key fields (illustrative) | Constraints |
| --- | --- | --- |
| `workload_identities` | tenant, id, SPIFFE ID nullable, trust-domain ID, workload/deployment/agent refs, owner, evidence kind, last seen | A logical agent and its runtime workload are distinct; unique identity within tenant/source/version, not globally by display name |
| `trust_domains` | tenant, name, issuer type, local/foreign, bundle digest, source, refresh time, freshness deadline | Store public trust metadata, not private signing keys; missing/stale bundle is explicit |
| `federation_links` | tenant, local and foreign domain refs, configured endpoint/reference, observed bundle version, state | Explicit configuration and evidence; no automatic cross-domain allow |
| `credential_observations` | tenant, workload ID, SVID type, issuer, nonsecret certificate fingerprint or token ID hash, issued/expiry, audience metadata, validation result, observed time | Never persist raw SVID, private key or bearer token; secret-bearing logs excluded |
| `attestation_bindings` | tenant, workload/deployment ref, source, selector evidence reference, observed version/time, confidence | Static declaration differs from observed and independently verified binding |
| `delegation_contexts` | tenant, workload, user subject, purpose, resource scope, issued/expiry, source session reference | Validate authenticated user and session; bounded lifetime and replay protections |
| `identity_policy_bindings` | tenant, identity, policy, scope, revision, effective/expiry | Identity authentication does not create permissions; changes invalidate decision caches |
| `identity_decisions` | tenant, request ID, principal, delegated user, action, resource ref, policy/source version, result, reason codes, evidence IDs, timestamp | Immutable, privacy-minimized; no prompt/source bytes, SVID or full secret-bearing paths |

Event history should include issue/renew/expire, failed validation, bundle update/failure, attestation drift, binding change, decision and remediation. Avoid claiming an instantaneous revocation state that the issuer/source cannot demonstrate; report freshness and observed rejection/expiry instead.

## 4. API contract to version after G0/G1

These paths are **proposed extension names**, not part of the current 19-operation `openapi.yaml`. Add them in a reviewed OpenAPI version with examples, typed client generation and tenant-scoped auth before wiring the browser.

| Method/path | Purpose and response boundary |
| --- | --- |
| `GET /api/v1/workload-identities` | Paginated, filtered inventory: kind, source, trust domain, evidence status, last seen, credential state; no raw credentials |
| `GET /api/v1/workload-identities/{id}` | Detail, nonsecret SVID metadata, deployment/agent/delegation refs, policy binding summaries, freshness and coverage |
| `GET /api/v1/workload-identities/{id}/events` | Paginated credential/attestation/decision event metadata with retention and access controls |
| `GET /api/v1/trust-domains` | Local/foreign inventory, bundle digest, source, refresh/freshness and explicit federation state |
| `GET /api/v1/identity-decisions/{id}` | Recorded decision trace with reason codes, policy/source revisions and masked evidence references |
| `POST /api/v1/identity-decisions/simulations` | Authorized analyst-only dry run, server-derived tenant and subject; no action execution and no raw SVID input |

Proposed simulation request:

```json
{
  "workload_identity_id": "fixture-workload-id",
  "delegated_subject_id": "fixture-user-id",
  "action": "rag.read",
  "resource_id": "fixture-payroll-index",
  "environment": "test",
  "at_time": "2026-09-29T00:00:00Z"
}
```

The server evaluates identity validation, delegation, policy and source ACL from trusted state. `at_time` is for simulation and must not let clients override production time in enforcement. Response includes `decision` (`allow|deny|unknown`), ordered checks with reason codes, evidence IDs, source/policy/bundle revisions, expiry and the limitation that this is a simulation. API errors follow the existing problem schema and never echo token or certificate content.

## 5. Backend implementation sequence

| Task | Start and deliverable | Live verification / pass and fail |
| --- | --- | --- |
| N01 Fixture semantics | Independently labeled identities, domains, bundles, agents, human delegations and allowed/denied expectations | Stable fixtures; wrong audience, stale bundle, absent user and explicit federation cases. Fail if expected decisions are generated by the evaluator under test |
| N02 Inventory ingest | Read-only adapter contract, normalize SPIRE/other issuer metadata without secrets; add migrations and API | Real test SPIRE source or controlled fixture adapter, tenant collision and partial enumeration. Fail if partial scan deletes unseen identities |
| N03 Credential verification | Validate X.509/JWT SVIDs against correct domain bundle, SAN/audience, validity and trust policy in the supported integration boundary | Invalid signature, wrong trust domain/audience, expired SVID, rotated key/bundle. Fail closed on unknown dependency. Do not make the catalog a general SVID minting service |
| N04 Workload and agent binding | Link attested workload/process to deployed artifact, agent, model, MCP tools and source paths with evidence confidence | Conflicting selectors, restarted pod, shared service account, stale deployment and duplicate display names. Fail if static code is labeled observed execution |
| N05 Delegated authorization | Policy decision point combines workload identity, bounded user delegation, action/tool/resource conditions and source ACL/freshness | Alice/Bob, wrong tool args, removed membership, expired session, stale ACL, replay and cache invalidation; verify forbidden bytes absent before model/tool |
| N06 SPIRE deployment adapter | Customer-hosted optional SPIRE connection with explicit read-only permissions and health/coverage receipt | Live Docker/Kubernetes test in customer-like environment; disconnect/reconnect, rotation and egress denial in local mode |
| N07 Vault integration (optional) | Separate adapter for incoming SPIFFE auth evidence or Vault-issued JWT-SVID metadata, per licensed deployment | Test auth method vs secrets engine direction separately, license/unavailable state, audience and tenant boundaries; do not make Vault required for OSS/local mode |
| N08 Federation and offline mode | Customer-approved bundle import/refresh, provenance, freshness, trusted local update bundle | Two domains, bundle rollover, stale foreign endpoint, no network egress, restore and clock skew. Fail if foreign identity automatically grants access |
| N09 Release gate | Browser/API/DB/log/model-boundary check on same commit and run ID | Real identity inventory, decision trace, denied retrieval before bytes, missing signal, restart/rotation, canary scan and role denial; fail on synthetic-only browser proof |

## 6. Required live tests

1. Start customer-like API, PostgreSQL, Keycloak and test SPIRE/identity issuer in disposable Docker/cluster resources with pinned digests. Use a fixed fixture seed, two tenants and a recorded UTC clock policy.
2. Issue an X.509-SVID for an allowed workload and a JWT-SVID with a scoped audience. Verify identity through the official libraries or supported ingress path; do not accept a browser-supplied SPIFFE ID as proof.
3. Attempt wrong trust domain, invalid signature, missing bundle, wrong JWT audience, expired SVID, clock skew, rotated bundle and issuer outage. Record deny/unknown and retry/freshness policy.
4. Bind an agent to a human context. Alice can retrieve the permitted synthetic document; Bob cannot. Inspect the actual model/tool fixture input and cached content to prove the denial occurred before forbidden bytes crossed the boundary.
5. Remove source permission or delegation while a session is active. Verify invalidation within the declared freshness bound and no stale cached allow. Repeat after API/worker restart and with concurrent tenant requests.
6. Run the browser workflow from identity inventory through domain, decision and data path. Compare UI, API, DB, audit event and source authorization state. Repeat at phone/tablet/desktop widths, keyboard and reduced motion.
7. In an air-gapped profile block all outbound network egress, import only signed/pinned local issuer/bundle updates, and repeat allowed and denied paths. A disconnected Vault endpoint must show unavailable rather than a green `connected` state.

**Success:** Supported paths have traceable identity and authorization evidence, negative paths fail safely, customer content and credentials stay in the boundary, and coverage gaps are visible. **Failure:** identity validation is equated to permission; unknown becomes allow; a stale bundle is silently trusted; a denied document reaches model input; token/key appears in logs, UI or artifacts; or a simulated browser result is called a live gate.

## 7. Primary references and distinction from the supplied article

- [SPIFFE ID and SVID specification](https://spiffe.io/docs/latest/spiffe-specs/spiffe-id/) and [SPIFFE Workload API](https://spiffe.io/docs/latest/spiffe-specs/spiffe_workload_api/).
- [SPIFFE trust domain and bundle](https://spiffe.io/docs/latest/spiffe-specs/spiffe_trust_domain_and_bundle/) and [federation](https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/).
- [SPIRE workload registration/attestation](https://spiffe.io/docs/latest/deploying/registering/).
- [Vault Enterprise SPIFFE authentication](https://developer.hashicorp.com/vault/docs/auth/spiffe/spiffe) and [Vault Enterprise SPIFFE secrets engine](https://developer.hashicorp.com/vault/docs/secrets/spiffe). The auth method consumes an incoming SVID to issue a Vault token; the secrets engine issues JWT-SVIDs to an already authenticated caller. Both are optional and require the appropriate license. The general NHI workflow does not depend on Vault.

Some high-level articles describe a SPIFFE ID as proving an agent's capabilities or trust level. Treat that as shorthand: the standard ID names a workload, while the product must evaluate separate policy and evidence to decide its allowed actions.
