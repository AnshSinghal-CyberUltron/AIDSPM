-- ZeroShield G1 reference schema for PostgreSQL 17+.
-- Review and translate into ordered Alembic migrations. Do not execute against
-- customer data as a substitute for migration/recovery testing.
-- UUIDs are application-generated. Current G0 `installations` remains separate.
-- No source content, plaintext secret or raw PII match is stored here.

CREATE TABLE tenants (
    id uuid PRIMARY KEY,
    display_name text NOT NULL CHECK (length(display_name) BETWEEN 1 AND 120),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Identity lookup only. The browser never queries this table. The auth service
-- uses a separate narrowly authorized database identity for issuer+subject lookup.
CREATE TABLE auth_subjects (
    id uuid PRIMARY KEY,
    issuer text NOT NULL,
    subject text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('human', 'workload')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (issuer, subject, kind)
);

CREATE TABLE tenant_memberships (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    auth_subject_id uuid NOT NULL REFERENCES auth_subjects(id),
    role text NOT NULL CHECK (role IN ('admin', 'analyst', 'viewer', 'remediation_approver')),
    active boolean NOT NULL DEFAULT true,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, auth_subject_id, role)
);

-- Store a keyed hash of the random opaque cookie, never the cookie itself.
-- CSRF secret is also stored hashed. Raw OIDC tokens do not belong here.
CREATE TABLE browser_sessions (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    auth_subject_id uuid NOT NULL REFERENCES auth_subjects(id),
    token_digest bytea NOT NULL UNIQUE,
    csrf_digest bytea NOT NULL,
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, id)
);
CREATE INDEX browser_sessions_active_idx ON browser_sessions (auth_subject_id, expires_at)
    WHERE revoked_at IS NULL;

CREATE TABLE sources (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    display_name text NOT NULL CHECK (length(display_name) BETWEEN 1 AND 120),
    connector_type text NOT NULL CHECK (connector_type = 'local_fixture'),
    approved_scope_ref text NOT NULL,
    config_ref text,
    secret_ref text,
    capability_version text NOT NULL,
    capabilities jsonb NOT NULL CHECK (jsonb_typeof(capabilities) = 'object'),
    state text NOT NULL CHECK (state IN ('enabled', 'disabled')),
    created_at timestamptz NOT NULL DEFAULT now(),
    disabled_at timestamptz,
    PRIMARY KEY (tenant_id, id),
    UNIQUE (tenant_id, connector_type, approved_scope_ref),
    CHECK (approved_scope_ref ~ '^fixture:[a-z0-9][a-z0-9_-]{0,63}$'),
    CHECK (secret_ref IS NULL),
    CHECK (capabilities ? 'can_write' AND capabilities->>'can_write' = 'false')
);
CREATE INDEX sources_page_idx ON sources (tenant_id, created_at DESC, id DESC);

CREATE TABLE scan_jobs (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    source_id uuid NOT NULL,
    status text NOT NULL CHECK (status IN
        ('queued', 'running', 'cancel_requested', 'completed', 'partial', 'failed', 'cancelled')),
    queued_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    finished_at timestamptz,
    lease_owner text,
    lease_until timestamptz,
    attempt integer NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    continuation_ref text,
    enumeration_complete boolean NOT NULL DEFAULT false,
    inspection_complete boolean NOT NULL DEFAULT false,
    eligible_count integer CHECK (eligible_count >= 0),
    inspected_count integer NOT NULL DEFAULT 0 CHECK (inspected_count >= 0),
    failed_count integer NOT NULL DEFAULT 0 CHECK (failed_count >= 0),
    unsupported_count integer NOT NULL DEFAULT 0 CHECK (unsupported_count >= 0),
    error_code text,
    created_by_subject_id uuid REFERENCES auth_subjects(id),
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id),
    CHECK (enumeration_complete OR eligible_count IS NULL),
    CHECK (NOT enumeration_complete OR eligible_count IS NOT NULL),
    CHECK (status <> 'completed' OR
        (enumeration_complete AND inspection_complete AND failed_count = 0
         AND unsupported_count = 0 AND finished_at IS NOT NULL)),
    CHECK (status NOT IN ('completed', 'partial', 'failed', 'cancelled') OR finished_at IS NOT NULL)
);
CREATE INDEX scan_jobs_claim_idx ON scan_jobs (status, lease_until, queued_at, id)
    WHERE status IN ('queued', 'running', 'cancel_requested');
CREATE INDEX scan_jobs_source_idx ON scan_jobs (tenant_id, source_id, queued_at DESC, id DESC);

CREATE TABLE assets (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    source_id uuid NOT NULL,
    native_key_digest bytea NOT NULL,
    asset_type text NOT NULL CHECK (asset_type IN ('file', 'rowset', 'collection')),
    display_name_masked text NOT NULL CHECK (length(display_name_masked) <= 200),
    lifecycle text NOT NULL CHECK (lifecycle IN ('active', 'deleted')),
    first_seen_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL,
    deleted_at timestamptz,
    last_full_scan_id uuid,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id),
    FOREIGN KEY (tenant_id, last_full_scan_id) REFERENCES scan_jobs(tenant_id, id),
    UNIQUE (tenant_id, source_id, native_key_digest),
    CHECK (last_seen_at >= first_seen_at),
    CHECK (lifecycle <> 'deleted' OR deleted_at IS NOT NULL)
);
CREATE INDEX assets_source_page_idx ON assets (tenant_id, source_id, first_seen_at DESC, id DESC);

CREATE TABLE asset_versions (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    asset_id uuid NOT NULL,
    source_version text,
    content_fingerprint bytea,
    metadata_fingerprint bytea NOT NULL,
    observed_at timestamptz NOT NULL,
    scan_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, asset_id) REFERENCES assets(tenant_id, id),
    FOREIGN KEY (tenant_id, scan_id) REFERENCES scan_jobs(tenant_id, id),
    UNIQUE (tenant_id, asset_id, scan_id)
);
CREATE INDEX asset_versions_asset_idx ON asset_versions (tenant_id, asset_id, observed_at DESC, id DESC);

CREATE TABLE scan_item_outcomes (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    scan_id uuid NOT NULL,
    native_key_digest bytea NOT NULL,
    asset_id uuid,
    status text NOT NULL CHECK (status IN ('inspected', 'failed', 'unsupported', 'skipped')),
    reason_code text NOT NULL,
    observed_at timestamptz NOT NULL,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, scan_id) REFERENCES scan_jobs(tenant_id, id),
    FOREIGN KEY (tenant_id, asset_id) REFERENCES assets(tenant_id, id),
    UNIQUE (tenant_id, scan_id, native_key_digest)
);
CREATE INDEX scan_outcomes_page_idx ON scan_item_outcomes (tenant_id, scan_id, observed_at DESC, id DESC);

CREATE TABLE evidence (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    kind text NOT NULL CHECK (kind IN ('declared', 'observed', 'source_verified', 'unknown')),
    origin text NOT NULL,
    producer_version text NOT NULL,
    collected_at timestamptz NOT NULL,
    expires_at timestamptz,
    limitations jsonb NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(limitations) = 'array'),
    masked_summary text,
    reference_digest bytea,
    source_id uuid,
    scan_id uuid,
    asset_version_id uuid,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id),
    FOREIGN KEY (tenant_id, scan_id) REFERENCES scan_jobs(tenant_id, id),
    FOREIGN KEY (tenant_id, asset_version_id) REFERENCES asset_versions(tenant_id, id),
    CHECK (expires_at IS NULL OR expires_at > collected_at)
);
CREATE INDEX evidence_freshness_idx ON evidence (tenant_id, collected_at DESC, expires_at);

CREATE TABLE classifications (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    asset_version_id uuid NOT NULL,
    label text NOT NULL CHECK (label IN ('public', 'internal', 'confidential', 'regulated')),
    detector_version text NOT NULL,
    detector_score numeric(5,4) CHECK (detector_score BETWEEN 0 AND 1),
    evidence_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, asset_version_id) REFERENCES asset_versions(tenant_id, id),
    FOREIGN KEY (tenant_id, evidence_id) REFERENCES evidence(tenant_id, id),
    UNIQUE (tenant_id, asset_version_id, label, detector_version)
);
CREATE INDEX classifications_label_idx ON classifications (tenant_id, label, asset_version_id);

CREATE TABLE ai_resources (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    name text NOT NULL CHECK (length(name) BETWEEN 1 AND 120),
    kind text NOT NULL CHECK (kind IN
        ('application', 'agent', 'rag_index', 'mcp_server', 'model_endpoint')),
    owner text NOT NULL,
    purpose text NOT NULL,
    approval text NOT NULL DEFAULT 'pending_review' CHECK (approval IN
        ('pending_review', 'approved', 'prohibited', 'exception', 'unknown')),
    lifecycle text NOT NULL DEFAULT 'configured' CHECK (lifecycle IN
        ('candidate', 'configured', 'deployed', 'observed_active', 'inactive', 'retired')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, id)
);
CREATE INDEX ai_resources_page_idx ON ai_resources (tenant_id, created_at DESC, id DESC);

-- Endpoint FKs protect graph structure. kind/object_id is a typed index into
-- domain tables; the service must validate the target and rebuild/check nodes.
CREATE TABLE graph_nodes (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    kind text NOT NULL CHECK (kind IN
        ('source', 'asset', 'ai_resource', 'principal', 'supporting_resource')),
    object_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, id),
    UNIQUE (tenant_id, kind, object_id)
);

CREATE TABLE graph_edges (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    from_node_id uuid NOT NULL,
    to_node_id uuid NOT NULL,
    relation text NOT NULL,
    decision text NOT NULL CHECK (decision IN ('allowed', 'denied', 'unknown')),
    evidence_id uuid NOT NULL,
    collected_at timestamptz NOT NULL,
    expires_at timestamptz,
    PRIMARY KEY (tenant_id, id),
    FOREIGN KEY (tenant_id, from_node_id) REFERENCES graph_nodes(tenant_id, id),
    FOREIGN KEY (tenant_id, to_node_id) REFERENCES graph_nodes(tenant_id, id),
    FOREIGN KEY (tenant_id, evidence_id) REFERENCES evidence(tenant_id, id),
    CHECK (expires_at IS NULL OR expires_at > collected_at)
);
CREATE INDEX graph_edges_from_idx ON graph_edges (tenant_id, from_node_id, relation, expires_at);
CREATE INDEX graph_edges_to_idx ON graph_edges (tenant_id, to_node_id, relation, expires_at);

CREATE TABLE findings (
    tenant_id uuid NOT NULL,
    id uuid NOT NULL,
    stable_key_digest bytea NOT NULL,
    source_id uuid,
    finding_type text NOT NULL,
    title text NOT NULL,
    rationale_masked text NOT NULL,
    severity text NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    status text NOT NULL CHECK (status IN
        ('open', 'triaged', 'accepted_risk', 'remediating', 'resolved', 'suppressed')),
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    first_seen_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL,
    suppression_reason text,
    suppression_expires_at timestamptz,
    verified_by_scan_id uuid,
    PRIMARY KEY (tenant_id, id),
    UNIQUE (tenant_id, stable_key_digest),
    FOREIGN KEY (tenant_id, source_id) REFERENCES sources(tenant_id, id),
    FOREIGN KEY (tenant_id, verified_by_scan_id) REFERENCES scan_jobs(tenant_id, id),
    CHECK (last_seen_at >= first_seen_at),
    CHECK (status <> 'resolved' OR verified_by_scan_id IS NOT NULL),
    CHECK (status <> 'suppressed' OR
        (suppression_reason IS NOT NULL AND suppression_expires_at IS NOT NULL))
);
CREATE INDEX findings_page_idx ON findings (tenant_id, first_seen_at DESC, id DESC);
CREATE INDEX findings_active_idx ON findings (tenant_id, status, severity, last_seen_at DESC);

CREATE TABLE finding_evidence (
    tenant_id uuid NOT NULL,
    finding_id uuid NOT NULL,
    evidence_id uuid NOT NULL,
    PRIMARY KEY (tenant_id, finding_id, evidence_id),
    FOREIGN KEY (tenant_id, finding_id) REFERENCES findings(tenant_id, id),
    FOREIGN KEY (tenant_id, evidence_id) REFERENCES evidence(tenant_id, id)
);

CREATE TABLE idempotency_records (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    actor_subject_id uuid NOT NULL REFERENCES auth_subjects(id),
    route_key text NOT NULL,
    key_digest bytea NOT NULL,
    request_digest bytea NOT NULL,
    response_status smallint NOT NULL,
    response_body jsonb NOT NULL CHECK (jsonb_typeof(response_body) = 'object'),
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, actor_subject_id, route_key, key_digest)
);
CREATE INDEX idempotency_expiry_idx ON idempotency_records (expires_at);

CREATE TABLE audit_events (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    id uuid NOT NULL,
    actor_subject_id uuid REFERENCES auth_subjects(id),
    action text NOT NULL,
    object_kind text NOT NULL,
    object_id uuid,
    result text NOT NULL,
    request_id uuid NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    details_masked jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(details_masked) = 'object'),
    PRIMARY KEY (tenant_id, id)
);
CREATE INDEX audit_events_time_idx ON audit_events (tenant_id, created_at DESC, id DESC);

-- Tenant RLS is defense in depth. The API must first validate OIDC identity,
-- active tenant membership and permissions, then in *each transaction* set:
-- SELECT set_config('zs.tenant_id', :trusted_tenant_uuid, true);
-- The role executing customer data queries is neither table owner nor BYPASSRLS.
-- The auth bootstrap role can only look up identity and memberships; it must
-- not receive direct grants on sources, assets, findings or evidence.
DO $$
DECLARE table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'tenant_memberships', 'browser_sessions', 'sources', 'scan_jobs',
        'scan_item_outcomes', 'assets', 'asset_versions', 'evidence',
        'classifications', 'ai_resources', 'graph_nodes', 'graph_edges',
        'findings', 'finding_evidence', 'idempotency_records', 'audit_events'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
        EXECUTE format(
            'CREATE POLICY %I ON %I USING (tenant_id = NULLIF(current_setting(''zs.tenant_id'', true), '''')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting(''zs.tenant_id'', true), '''')::uuid)',
            table_name || '_tenant', table_name
        );
    END LOOP;
END $$;

-- The tenant root table uses id rather than tenant_id. A general API SELECT
-- grant must still see only the selected verified tenant.
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants FORCE ROW LEVEL SECURITY;
CREATE POLICY tenants_current ON tenants
    USING (id = NULLIF(current_setting('zs.tenant_id', true), '')::uuid)
    WITH CHECK (id = NULLIF(current_setting('zs.tenant_id', true), '')::uuid);

-- Production grants, auth bootstrap policy, worker scoping and migration owner
-- are provisioned separately. Do not connect the API with an owner/superuser.
-- Test SELECT/INSERT/UPDATE/DELETE and pooled-session reuse as the actual role.
