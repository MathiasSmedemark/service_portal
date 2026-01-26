-- Role bindings table (Delta).
-- Deploy with catalog.schema qualification per AGENTS.md.
CREATE TABLE IF NOT EXISTS role_bindings (
    id STRING NOT NULL,
    platform_id STRING,
    principal_type STRING NOT NULL,
    principal_id STRING NOT NULL,
    role STRING NOT NULL,
    state STRING NOT NULL,
    created_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by STRING NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
USING DELTA;
