# Foundation execution cards: T02–T08

This is a current-repository companion to the full T01–T64 plan. It gives the first developer a practical path through the existing scaffold. **T01's written scope exists; no foundation feature is claimed verified.** Use a branch and a disposable local environment. Never seed or reset a customer database. The file locations below follow the actual repository tree, which differs in places from the original greenfield plan.

## Shared test protocol

1. Record the commit SHA and clean/dirty status. Use committed `uv.lock`, `pnpm-lock.yaml` and pinned image digests.
2. Use a unique run ID per check, disposable Compose project/volumes and fixed synthetic fixture seed. Create `artifacts/<task>/<run-id>/manifest.json` with test count, versions, scope, actual commands, pass/fail, limitations and hashes of sanitized evidence.
3. Run unit/contract checks; then the task's live PostgreSQL/IdP/API/worker checks. When a UI exists, test a real browser against those same services. An HTTP mock cannot satisfy a live acceptance check.
4. Inject at least one failure: restart, denied role, malformed input or partial source outcome as appropriate. Record both the expected and observed state.
5. A gate returns nonzero for missing, unimplemented, zero-collected, required-skipped, failed, timed-out or interrupted checks. Cleanup can remove only a run-scoped disposable project.

Commands shown are **targets to implement and run**, not assertions that the current repository supports them. The current runner uses `make verify CHECK=<slug>`; the older plan's `TASK=Txx` examples require a mapping or documentation correction.

## T02 — Make the pinned toolchain reproducible

**Start:** `pyproject.toml`, `uv.lock`, all Python workspace `pyproject.toml` files, `apps/web/package.json`, `pnpm-lock.yaml`, `Makefile`, `scripts/doctor.py`, `ops/images.lock.json`.

**Work in order**

1. Define one supported development matrix for Python 3.12, Node 24, pnpm, Docker Compose and amd64/arm64. Verify the exact image digests and package resolution on supported machines. Do not put developer passwords in `.env.example`.
2. Make `uv sync --frozen --all-packages --group dev` build all workspace packages. Add `py.typed` package markers or configure mypy to type-check the source tree correctly. Remove current Ruff errors in `scripts/evidence.py`, `scripts/verify.py`, `scripts/validate_contract.py` and tests.
3. Make `make build` actually build the Python packages, web bundle and required container images. Pulling base images alone is not a container build.
4. Choose and document one pinned way to invoke Node/pnpm (for example a pinned toolchain in CI and a documented local installation); keep `doctor` aligned. Validate lockfile immutability and the declared two CPU architectures where available.
5. Add CI jobs for frozen install, lint, typecheck, contract validation and tests. CI must report the commit and tool versions.

**Verify:** On a clean checkout run `make doctor`, `uv sync --frozen --all-packages --group dev`, `make lint`, `make typecheck`, `make build`. Deliberately desynchronize a lockfile in a disposable branch and confirm frozen install fails. Run the web build with the exact supported Node/pnpm versions. Docker is not needed to claim Python package installation but is required to verify container images.

**Pass:** Both clean builds and negative lockfile test behave as specified; no host cache, floating version or hidden secret is necessary. **Fail:** Ruff/mypy failure, only base-image pulls, an undocumented local dependency, or a green gate without running the build. **Current evidence:** local Python workspace sync and six harness tests passed; Ruff reported 16 issues; mypy failed on a missing typed-package marker. The review machine lacked Docker and had older Node/pnpm pins, so it could not certify a full clean build.

## T03 — Make verification and evidence trustworthy

**Start:** `tests/task_registry.yaml`, `scripts/verify.py`, `scripts/evidence.py`, `tests/harness/`, `Makefile`.

**Work in order**

1. Make task and phase semantics explicit: `make verify CHECK=...` runs one check; `make gate PHASE=...` must examine **all required checks**, including unimplemented ones. A phase cannot pass while `first-live-stack` or tenant isolation is unimplemented. Honor registry prerequisites and execute the declared command rather than silently substituting a narrower check.
2. Use collision-resistant run IDs, with one run identity per check. The current timestamp-only ID can be reused within a second; the foundation gate was observed overwriting `artifacts/runs/<id>/compose-project.json`. Create manifests atomically and never reuse a Compose project between concurrent checks.
3. Record actual process status, collected test count, required skips, timeouts, profile, service versions and hashes. Distinguish `not_applicable` from `not_run` and `passed`. Treat a runner crash as failure, not an empty success.
4. Restrict retained evidence to structured, allowlisted metadata. Current regex sanitization misses synthetic Basic credentials and `postgresql+psycopg://` DSNs. Redact or omit sensitive values *before* they enter a retained log, artifact, screenshot or HTML report.
5. Add tests for a passing sentinel, failing sentinel, zero collection, missing file, timeout, subprocess failure, partial artifact and interrupted cleanup. Ensure one check cannot overwrite another check's manifest.

**Verify:** Run `make verify CHECK=verify-harness`; prove exit 0/1/2/3 paths, an unimplemented foundation gate exits nonzero, two checks launched together retain separate run IDs, and synthetic canaries/credentials do not appear anywhere in retained evidence. Run with an empty test selector and a failed child process. Browser evidence is `not_applicable` until T04, never `passed`.

**Pass:** A green phase means every required task passed with verifiable evidence. **Fail:** An excluded unimplemented task allows a green phase, test count zero returns success, two runs collide, or a synthetic secret is retained. **Hard constraint:** The evidence mechanism itself must not become a second sensitive-data store.

## T04 — First live API, PostgreSQL and browser round trip

**Start:** `apps/api/src/ai_dspm_api/`, `apps/api/Dockerfile`, `apps/web/Dockerfile`, `apps/web/src/`, `ops/compose/compose.yml`, `openapi.yaml`, `tests/`.

**Work in order**

1. Create API and web Dockerfiles with pinned base images and reproducible dependency installation. Bind external development ports to loopback. Keep secrets out of image layers and JavaScript bundles.
2. Implement FastAPI app creation and the exact G0 HTTP contract: `/livez`, `/readyz`, `/api/v1/system`. Align the Compose health check with the chosen liveness route. Liveness reports process health; readiness performs a bounded PostgreSQL query and returns unavailable on DB outage.
3. Add a reviewed migration for a harmless installation identity. Persist the ID once in PostgreSQL; do not regenerate it on each API boot. Return installation ID, build revision and supported scope from the server, with no customer data on an unauthenticated health path.
4. Reverse-proxy browser requests to the internal API service. The System screen fetches it and has loading, ready and unavailable states. API reconnect must recover after a backend restart without restarting the web container.
5. Add API integration tests and a Playwright browser test against Compose. Compare the ID in database, API and UI. Refresh and restart API; then stop PostgreSQL to prove readiness/UI failure and recovery.

**Verify:** From fresh disposable volumes: build and start Compose; inspect service health; query live endpoints; use Playwright at the browser URL; restart API; stop and restart DB. Repeat once with fresh volumes. Capture HTTP status, database row, browser state and sanitized logs under one run ID.

**Pass:** A live install ID matches DB/API/UI and survives API restart; DB outage fails readiness and cannot show a stale ready badge; recovery is automatic. **Fail:** missing Dockerfile, static ID, fake success indicator, health route mismatch, or proxy requires manual restart. **Boundary:** No source content or tenant-scoped data is exposed before T05/T06.

## T05 — Tenant storage and isolation

**Start:** `schema.postgres.sql` and `roles.example.sql` as references; implement reviewed Alembic migrations in the API/data package, restricted runtime DB roles and repository access functions. Do not run reference DDL directly against production.

**Work in order:** Migrate tenants, principals/membership, sources, assets, jobs, evidence and finding records needed by G1. Use composite tenant-aware foreign keys where applicable, RLS policies and separate migration owner/API/worker/auth roles. Set trusted tenant context transaction-locally. Deny when context is absent; make pooling safe across tenant changes. Enforce application authorization in addition to RLS.

**Verify:** Against *live PostgreSQL* under the actual restricted runtime role, create Alpha and Beta with colliding native source IDs. Test read, insert, update, join and foreign-key reference attempts across tenants. Alternate Alpha/Beta on one pooled connection, clear tenant context, and repeat. Run migrations on a clean database and rehearse a forward-only recovery from a test snapshot. Browser System should still work after migration.

**Pass:** Every covered cross-tenant operation denies and no pooled context leaks. **Fail:** tests use only a superuser; a guessed UUID, join or background job crosses the boundary; a missing tenant defaults to a tenant. **Do not proceed to ingestion** on failure.

## T06 — OIDC sessions and backend authorization

**Start:** Keycloak development realm, API auth/session module, backend permission matrix and browser auth state. Do not use a homemade password table.

**Work in order:** Authorization code + PKCE; validate signature, issuer, audience, expiry and relevant claims; map external subject to server-side memberships; issue opaque HttpOnly app sessions with CSRF defenses for state changes; rotate on login and revoke on logout. Distinguish humans from workload identities. Define admin, analyst, viewer and remediation-approver actions in the API; UI affordances follow backend decisions.

**Verify:** With live Keycloak, DB, API and browser, sign in as each role, refresh, log out, open a direct protected URL and test expired session. Send forged tenant headers, wrong-audience/wrong-issuer tokens and removed membership. The hidden Add Source button must correspond to an API denial.

**Pass:** Correct roles are allowed, wrong roles/tokens denied, removed membership takes effect within a declared window, and logout invalidates the app session. **Fail:** UI hiding alone enforces access; unsigned token or client tenant claim is trusted; production mode accepts a dev token.

## T07 — Deterministic synthetic corpus

**Start:** `fixtures/` and `tests/`. Existing `examples/` are API response examples, not an independent scanner oracle.

**Work in order:** Seed two tenants, Alice/Bob, HR Bot, payroll, normal files and negatives from a fixed seed. Include text, CSV, JSON, text PDF, encrypted/image-only PDF, malformed and oversized inputs. Maintain expected classification spans and ACL outcomes in a separate manually reviewed manifest; never generate expected results by invoking the detector under test. Add checksums, fixture version and safe disposal guards.

**Verify:** Seed two fresh Compose projects using the same seed; compare checksums and expected IDs. Repeat seeding in one project and confirm idempotence. Attempt to seed outside the test marker and require refusal. Validate expected byte/character spans independently.

**Pass:** Stable corpus, independently labeled expectations and no real customer secrets. **Fail:** hidden nondeterminism, detector-generated ground truth or destructive seeding reachable from production.

## T08 — Privacy, secrets and audit baseline

**Start:** API logging middleware, secret-provider interface, audit event schema/migration, artifact policy and browser error flows. Complete this before ingesting source content.

**Work in order:** Allowlist log fields; exclude raw requests, cookies, authorization headers, connection strings, source text and sensitive filenames. Store references to mounted/customer-managed secrets, not plaintext credentials in catalog responses. Add access-denial and configuration-change audit records with actor/action/outcome/revision. Use tenant-keyed HMAC for low-entropy correlation, with key rotation and retention semantics. Set retention and access policies for temporary extraction and artifacts.

**Verify:** Inject synthetic canaries into source/configuration errors, expired sessions and malformed inputs. Exercise live API/browser paths; inspect logs, traces, DB fields, network captures, generated reports and screenshots for canaries. Rotate a test secret reference without rebuilding images. Restart services and repeat.

**Pass:** No unauthorized plaintext retained or returned; audit has complete safe metadata; key/secret rotation works. **Fail:** stack traces include source bytes, credentials can be read back, a report leaks cookies, or deletion only removes a UI row. Repair the originating logging path, remove tainted artifacts and rerun the leak suite.

## Foundation exit gate

The foundation phase is complete only when T02–T08 checks are genuinely runnable and pass on the same recorded commit, from a clean build and fresh disposable volumes. At minimum attach: image/lock hashes, migrations, restricted-role tenant negative tests, real IdP session tests, browser System/outage screenshots, clean lint/typecheck, canary search results, recovery observations, and a list of unsupported behavior. A missing live service is `Blocked`, not `Verified`.
