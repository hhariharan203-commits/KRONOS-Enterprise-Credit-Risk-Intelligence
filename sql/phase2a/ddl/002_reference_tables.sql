CREATE TABLE IF NOT EXISTS reference.dim_temporal_classification (
    classification_code VARCHAR PRIMARY KEY,
    description VARCHAR NOT NULL,
    historical_analytics_eligible BOOLEAN NOT NULL,
    regulatory_claim_eligible BOOLEAN NOT NULL,
    active_flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_snapshot_status (
    snapshot_status_code VARCHAR PRIMARY KEY,
    description VARCHAR NOT NULL,
    terminal_flag BOOLEAN NOT NULL,
    active_flag BOOLEAN NOT NULL
);
