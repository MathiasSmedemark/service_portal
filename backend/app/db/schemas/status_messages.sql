-- Manual status messages (Delta).
-- Replace <catalog>.<schema> with your UC catalog/schema before execution.
-- Assumptions:
-- - state uses draft/published/archived.
-- - platform_tags holds platform ids or tags; empty/null means global.
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.status_messages (
    id STRING NOT NULL,
    platform_id STRING,
    platform_tags ARRAY<STRING>,
    severity STRING NOT NULL,
    title STRING NOT NULL,
    body_md STRING NOT NULL,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
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
