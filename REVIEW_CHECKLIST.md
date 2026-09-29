# What to send for GitHub review

Share the repository URL and PR or commit SHA, the frontend Git sync branch/revision, and
which task IDs you claim (`T04`, `T05`, etc.). Do not share credentials or customer content.

For each claimed task, include:

| Evidence | Minimum content |
| --- | --- |
| Contract | OpenAPI diff, generated TS client diff, compatibility note |
| Database | Alembic migration, actual role grants/RLS, fresh DB upgrade and repeat result |
| Unit | Meaningful behavior/negative tests, nonzero test count |
| Live | Docker Compose logs/commands with real Postgres, IdP and worker when required |
| Browser | Playwright flow against live backend without mocked required API responses |
| Security | Two tenant collision, forged tenant/header, wrong audience, source write denial, masked canary leak search as applicable |
| Recovery | Backend restart; worker kill/retry; partial source listing; restore rehearsals at later gates |
| Provenance | Git SHA, dependency lock hash, image digests, fixture seed, run ID, sanitized evidence hashes |

Review gate examples:

1. `T04`: install ID equals the database row and survives API restart; DB outage makes
   `/readyz` and System unavailable; recovery works.
2. `T05`: actual restricted DB role cannot read/write/link tenant B while tenant A is selected;
   a pooled connection alternating tenants has no leaked context.
3. `T06`: expired session, wrong OIDC audience and removed membership deny backend requests;
   browser logout and direct URL both behave correctly.
4. `T15`: a partial enumeration cannot tombstone unseen assets and unsupported files are counted.
5. `T18`: login → source → scan → assets → finding → rescan works end to end without API mocks.
6. `T26`: inspect actual model fixture input to prove Bob's forbidden content was never sent;
   changing an ACL revokes Alice within the declared freshness rule.

Status vocabulary: `Planned`, `In progress`, `Verified`, or `Blocked` with reason. A build,
schema parse, mocked browser test or green UI badge alone does not mean `Verified`.

Expected PR note format:

```text
Task: T05 tenant isolation
Scope: schema migration, transaction context, repository guards, tests
Run: <run-id>   Commit: <sha>   Fixture seed: <seed>
Live services: PostgreSQL <image digest>, API <image digest>
Pass: <named assertions>
Fail/blocked: <named assertions or none>
Known limits: <supported/unsupported scope>
Evidence: <sanitized paths or hashes>
```

