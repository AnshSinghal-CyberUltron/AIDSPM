# ZeroShield AI DSPM — API and database contract v0.1 (draft)

This package is for **you to implement**, then sync to GitHub for code review. It defines the
first real read-only posture MVP in depth and reserves later product layers. No route or
database table in this package is proof that the corresponding product feature works.



## Development toolchain

Supported local tools are pinned. `scripts/doctor.py` rejects a different Node or pnpm major.

| Tool           | Pin                                                                                | How to invoke it                                                          |
| -------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Python         | 3.12.14                                                                            | `uv run --python 3.12`                                                  |
| uv             | 0.11.26 on the developer machine;`0.12.15` digest inside `apps/api/Dockerfile` | `uv lock --check` then `uv sync --frozen --all-packages --group dev`  |
| Node           | 24.21.0                                                                            | `node` on `PATH`, matching `apps/web/package.json` `engines`      |
| pnpm           | 12.4.2                                                                             | `corepack prepare pnpm@12.4.2 --activate`, then `pnpm --dir apps/web` |
| Docker Compose | Compose v2 with the Docker CLI                                                     | `docker compose`                                                        |

Image digests live in `ops/images.lock.json`. Python, Node, Nginx, and uv are digest-pinned in the Dockerfiles. This repository has built `ai-dspm-api:dev` and `ai-dspm-web:dev` on linux/amd64. The linux/arm64 digests in the lock file are recorded and have not been built on that architecture.

Do not put database passwords, admin passwords, or `AIDSPM_DEV_TOKEN` values in `.env.example`. Real values stay in an untracked `.env`.

Checks:

```bash
uv lock --check
uv sync --frozen --all-packages --group dev
pnpm --dir apps/web install --frozen-lockfile
make lint
make typecheck
uv run --python 3.12 python scripts/validate_contract.py
uv run --python 3.12 pytest tests/harness -q
make build
```

## Read in this order

1. [`API_GUIDE.md`](API_GUIDE.md): behaviors, permission matrix, examples, release order.
2. [`openapi.yaml`](openapi.yaml): machine-readable G0/G1 HTTP paths and JSON schemas.
3. [`DB_GUIDE.md`](DB_GUIDE.md): entity meaning, isolation, job leases and migrations.
4. [`schema.postgres.sql`](schema.postgres.sql): PostgreSQL **reference DDL**, to translate into
   reviewed Alembic migrations, not paste over a production database.
5. [`roles.example.sql`](roles.example.sql): separate auth, API and scanner runtime grant model.
6. [`REVIEW_CHECKLIST.md`](REVIEW_CHECKLIST.md): evidence needed when you share a GitHub PR.
7. [`FUTURE_MODULES.md`](FUTURE_MODULES.md): full AI lifecycle, shadow AI, code-to-cloud,
   RAG, runtime, remediation, retirement and offline extension map.
8. [`examples/`](examples/): synthetic sample responses. They are not customer observations.

## Scope and existing code

The prior `ZeroShield_Python_Backend_G0.zip` implemented only system/liveness/readiness and
was not live-tested here. Its FastAPI default errors and development database role need
updating to this contract before tenant data exists. The current Lovable console is still
primarily a synthetic frontend. Connect a **fresh Git-synced revision**, beginning with System.

The older implementation plans retain full-scope task identifiers T01–T64, D01–D22, L01–L32,
A01–A14, C01–C08 and R01–R60. This pack is a precise first-slice contract, not an assertion
that one OpenAPI file covers every future connector, risk or lifecycle state. G2 authorization,
runtime, remediation and offline deployment need separately versioned extensions and live tests.

## Local document validation

With Python 3.12 and PyYAML installed:

```bash
python scripts/validate_contract.py
```

This checks YAML/JSON parsing, duplicate YAML mapping keys, local OpenAPI references,
operation IDs, seven example payloads against a limited schema subset, and SQL/table
references. It is **structural**.
Also run a full OpenAPI 3.1 validator and real PostgreSQL migration suite in your repo.
Neither a structural check nor an SQLite test counts as a live PostgreSQL gate.

**Validation performed for this draft:** the structural script passed (19 operations,
7 examples), Python syntax parsed, and local document links resolved. A full OpenAPI
semantic validator and live PostgreSQL DDL/role tests were unavailable in the authoring
environment. No endpoint beyond the prior G0 prototype was executed here.

## Implementation order

`G0 System` → `T05 tenancy` → `T06 OIDC roles` → `T07–T10 fixtures/connector`
→ `T11–T15 worker/coverage` → `T16–T18 findings/browser MVP`
→ `T19–T26 protected RAG`. Develop on reviewed branches and retain a runnable frontend.

**Questions to settle during implementation:** actual OIDC issuer and cookie deployment origin;
auth bootstrap DB grants; approved fixture mount map; HMAC key provider/rotation; retention;
and the current Lovable Git sync repository branch. These do not block reading or starting G0.
