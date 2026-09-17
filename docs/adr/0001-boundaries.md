
# ADR 0001 — Customer processing boundary and first product slice

Status: Accepted
Date: 2026-09-16
Product: AI DSPM
Task: T01

## Context

AI DSPM must show which sensitive data AI can reach, explain the evidence, and later enforce access at integrations the customer controls. Content, prompts, embeddings, credentials and finding values can all be sensitive. A hosted classifier that leaves the customer environment by default would violate the product claim.

## Decision

1. Run UI, API, catalog, workers, policy evaluation, model adapters, retrieval, secret references and evidence storage inside the customer environment.
2. Do not export prompts, source text, embeddings, credentials or sensitive finding values to a product vendor by default.
3. Treat an external LLM as optional and as a data-leaving-the-boundary event, even if the rest of the stack is customer-hosted.
4. Use a deterministic local model fixture as the default for reproducible tests.
5. Ship a read-only posture MVP (T18) before runtime blocking (T26+).
6. Start with one modular backend, FastAPI + PostgreSQL + React, Docker Compose, Keycloak in development.
7. Use declared, observed and verified access as distinct evidence kinds. Missing evidence is `unknown`, never silent `allowed` on protected retrieval.

## Consequences

- First connector is a local filesystem fixture, not a cloud inventory product.
- Scanner credentials are read-only; remediation uses a different identity later.
- Tests must include egress-deny and canary searches of logs, traces, URLs and artifacts (H01, H05).
- UI copy must show coverage limits; H15 forbids universal security claims.

## Alternatives rejected

- Vendor-hosted prompt inspection as the default path
- Starting with Kubernetes or a large connector catalog
- Homemade passwords / unsigned identity headers
- Treating posture findings as proof of runtime blocking
