-- Status ingestion runs (Delta).
-- Replace <catalog>.<schema> with your UC catalog/schema before execution.
-- Assumptions:
-- - state uses RUNNING/SUCCESS/FAIL.
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.status_ingestion_runs (
    id STRING NOT NULL,
    source STRING NOT NULL,
    state STRING NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    error_summary STRING,
    error_payload STRING,
    created_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by STRING NOT NULL
)
USING DELTA;
