CREATE TABLE IF NOT EXISTS core.dim_historical_entity (
    entity_key VARCHAR PRIMARY KEY,
    source_system VARCHAR NOT NULL,
    identity_grain VARCHAR NOT NULL,
    source_entity_id VARCHAR NOT NULL,
    first_observed_date DATE NOT NULL,
    last_observed_date DATE NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(source_system, identity_grain, source_entity_id)
);

CREATE TABLE IF NOT EXISTS core.dim_historical_facility (
    facility_key VARCHAR PRIMARY KEY,
    entity_key VARCHAR NOT NULL,
    source_system VARCHAR NOT NULL,
    source_facility_id VARCHAR NOT NULL,
    first_observed_date DATE NOT NULL,
    last_observed_date DATE NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(source_system, source_facility_id)
);

CREATE TABLE IF NOT EXISTS core.dim_historical_snapshot (
    historical_snapshot_key VARCHAR PRIMARY KEY,
    snapshot_id VARCHAR NOT NULL UNIQUE,
    source_asset_id VARCHAR NOT NULL,
    temporal_contract_id VARCHAR NOT NULL,
    temporal_contract_version VARCHAR NOT NULL,
    ingestion_batch_id VARCHAR NOT NULL,
    snapshot_date DATE NOT NULL,
    snapshot_date_type VARCHAR NOT NULL,
    history_mode VARCHAR NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    identity_grain VARCHAR NOT NULL,
    identity_continuity_status VARCHAR NOT NULL,
    source_run_inventory_json VARCHAR NOT NULL,
    source_model_inventory_json VARCHAR NOT NULL,
    source_sha256 VARCHAR NOT NULL,
    canonical_schema_hash VARCHAR NOT NULL,
    temporal_quality VARCHAR NOT NULL,
    storage_readiness_status VARCHAR NOT NULL,
    loaded_at TIMESTAMP NOT NULL
);
