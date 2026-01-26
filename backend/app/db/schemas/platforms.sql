-- Platforms table (Delta).
-- Replace <catalog>.<schema> with your UC catalog/schema before execution.
-- Assumptions:
-- - state captures lifecycle (active/inactive/retired); health comes from status_results.
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.platforms (
    id STRING NOT NULL,
    name STRING NOT NULL,
    domain STRING NOT NULL,
    owner_group STRING NOT NULL,
    description STRING,
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
