-- Status check definitions (Delta).
-- Replace <catalog>.<schema> with your UC catalog/schema before execution.
-- Assumptions:
-- - state captures lifecycle (enabled/disabled).
-- - warn_after_minutes < crit_after_minutes and all thresholds are > 0.
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.status_checks (
    id STRING NOT NULL,
    platform_id STRING NOT NULL,
    name STRING NOT NULL,
    check_type STRING NOT NULL,
    owner_group STRING,
    description STRING,
    sla_minutes INT NOT NULL,
    warn_after_minutes INT NOT NULL,
    crit_after_minutes INT NOT NULL,
    state STRING NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by STRING NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by STRING
)
USING DELTA;
