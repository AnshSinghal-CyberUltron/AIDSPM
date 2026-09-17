
# AI DSPM — MVP capability contract

Product: AI DSPM
Contract version: 0.1.0-contract
Status: T01 — not a running system

This document is the human-readable twin of `docs/scope.json`. If they disagree, `docs/scope.json` wins after a reviewed revision of both.

## What the first two releases are

### P1 read-only posture (gate T18)

An operator authenticates with Keycloak, registers a read-only local filesystem fixture, starts a scan, sees inventory and coverage, inspects masked classifications and findings, and follows declared application **HR Bot** to payroll. A rescan updates findings without duplication. Failed and unsupported files stay visible.

P1 does not block a model. P1 does not know arbitrary cloud IAM.

### P2 protected RAG (gate T26)

HR Bot uses a separate PostgreSQL/pgvector source. **Alice** retrieves a synthetic payroll document. **Bob** does not. Authorization runs before forbidden chunk bytes reach the application or the model. The UI cites source version and authorization evidence. Revocation and dependency-failure tests must pass.

## Future demo clicks (not executable until T18 / T26)

### T18 operator demo

1. Open the console on loopback.
2. Sign in as operator via Keycloak (no homemade password form).
3. Register source type `filesystem` with an approved fixture root reference, not a raw browser path.
4. Start scan; wait on persisted status, not a fake spinner.
5. Open inventory; confirm coverage denominator and unsupported/failed reasons.
6. Open a finding; confirm evidence is masked; confirm no raw payroll salary in DOM, network, or download.
7. Open AI asset **HR Bot**; see declared binding to payroll (evidence kind: declared).
8. Change one fixture file; rescan; confirm finding identity is stable and not duplicated.
9. Confirm encrypted and image-only PDFs appear as incomplete coverage, not as clean.

### T26 Alice / Bob demo

1. Sign in as Alice; ask HR Bot a question that requires the payroll document; receive an answer grounded in allowed chunks.
2. Sign in as Bob; ask the same question; see a denial; confirm payroll bytes are absent from retrieved content, model-fixture input, caches, and UI.
3. Open the explanation panel; see source version, ACL revision, policy revision, and evidence kind.
4. Revoke Bob if any stale allow existed; confirm deny after the freshness boundary.
5. Stop the source database; confirm protected retrieval fails closed, not open.

## Nine questions — first honest answer

| ID | Question                                    | First phase                | Until then the UI must say                                                   |
| -- | ------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------- |
| Q1 | What sensitive data can an AI agent access  | P2 (agents in P4)          | Unknown without identity, tools, permissions, classification, and a path     |
| Q2 | Which RAG stores contain regulated data     | P2 pgvector (P5 Qdrant)    | Unknown if payload/provenance is missing; embeddings are not the source text |
| Q3 | Which employees send sensitive data to AI   | P3 (P5 managed employee)   | Unmanaged traffic is outside coverage                                        |
| Q4 | Which agents have excessive permissions     | P4                         | Unused is not the same as unnecessary                                        |
| Q5 | What sensitive data enters a prompt         | P3                         | Unseen paths are excluded or blocked, not scanned                            |
| Q6 | What sensitive data an LLM returns          | P3                         | Not a zero-leak guarantee; sent bytes cannot be retracted                    |
| Q7 | Which MCP tool can access confidential data | P4                         | Tool descriptions are untrusted                                              |
| Q8 | Can an agent retrieve what the user cannot  | P2 (delegated P4)          | Missing/stale context is deny on protected paths                             |
| Q9 | Redact / block / mask automatically         | P3 (source remediation P6) | P1 is posture only                                                           |

## Exclusions that must remain visible in the product

- Arbitrary SaaS visibility
- Image inspection before an OCR adapter exists
- Universal IAM equivalence across clouds
- Model training
- Production scalability promises
- Vendor export of customer content by default

Later in-scope, not in this MVP: S3, Qdrant, customer PostgreSQL scanning, Microsoft Graph/SharePoint/OneDrive, Copilot audit, managed employee coverage.

## Wording that is forbidden until evidence exists

Do not say: zero leak, full visibility, complete compliance, or exact effective access for every identity system.
