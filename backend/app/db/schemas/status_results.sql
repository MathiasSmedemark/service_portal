-- Status check results (append-only time series, Delta).
-- Replace <catalog>.<schema> with your UC catalog/schema before execution.
-- Assumptions:
-- - state stores health (green/yellow/red/unknown).
-- - measured_at is observation time; created_at is ingestion time.
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.status_results (
    id STRING NOT NULL,
    check_id STRING NOT NULL,
    platform_id STRING NOT NULL,
    state STRING NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    observed_value STRING,
    message STRING,
    error_payload STRING,
    ingestion_run_id STRING,
    created_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by STRING NOT NULL
)
USING DELTA;
