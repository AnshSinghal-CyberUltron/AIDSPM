-- Reference privileges for a disposable integration environment.
-- Review with your DBA/security owner and translate into deployment migrations.
-- Login identities and credentials must be provisioned by your secret manager;
-- these are NOLOGIN group roles, never the runtime credentials themselves.
-- Run after schema.postgres.sql. This is NOT an automatically verified grant set.

CREATE ROLE zs_auth NOLOGIN;
CREATE ROLE zs_app NOLOGIN;
CREATE ROLE zs_worker NOLOGIN;

-- The auth bootstrap service validates OIDC issuer/signature/audience/expiry
-- before issuer+subject lookup. It alone may enumerate memberships/sessions
-- across tenants; it has no product catalog grants.
GRANT SELECT ON auth_subjects, tenant_memberships, browser_sessions TO zs_auth;
GRANT INSERT ON auth_subjects, browser_sessions TO zs_auth;
GRANT UPDATE (revoked_at, expires_at) ON browser_sessions TO zs_auth;
CREATE POLICY tenant_memberships_auth_lookup ON tenant_memberships
    FOR SELECT TO zs_auth USING (true);
CREATE POLICY browser_sessions_auth_lookup ON browser_sessions
    FOR SELECT TO zs_auth USING (true);
-- Session creation/revocation uses a verified tenant and transaction-local
-- zs.tenant_id. The tenant policy in schema.postgres.sql applies to writes.

GRANT SELECT ON tenants, tenant_memberships, sources, scan_jobs,
    scan_item_outcomes, assets, asset_versions, evidence, classifications,
    ai_resources, graph_nodes, graph_edges, findings, finding_evidence,
    idempotency_records, audit_events TO zs_app;

-- Exact column-level service permissions are also checked in the API.
GRANT INSERT, UPDATE ON sources, scan_jobs, findings, ai_resources,
    graph_nodes, graph_edges, idempotency_records TO zs_app;
GRANT INSERT ON evidence, finding_evidence, audit_events TO zs_app;

GRANT SELECT ON sources, scan_jobs, scan_item_outcomes, assets,
    asset_versions, evidence, classifications, ai_resources, graph_nodes,
    graph_edges, findings, finding_evidence TO zs_worker;
GRANT INSERT, UPDATE ON scan_jobs, scan_item_outcomes, assets, findings,
    graph_nodes, graph_edges TO zs_worker;
GRANT INSERT ON asset_versions, evidence, classifications,
    finding_evidence, audit_events TO zs_worker;

-- No DELETE privilege is granted to any runtime role. In particular, neither
-- zs_app nor zs_worker can UPDATE/DELETE asset_versions, evidence or audit_events.
-- Retention/legal-hold cleanup gets a separately audited role when specified.
-- Neither zs_app nor zs_worker may own these tables or have BYPASSRLS.
-- Bind dedicated LOGIN roles to exactly one group role per process. Test
-- catalog access and RLS with these runtime identities, not a superuser.
