CREATE TABLE IF NOT EXISTS control.platform_release (
    release_id VARCHAR PRIMARY KEY,
    phase_name VARCHAR NOT NULL,
    release_version VARCHAR NOT NULL,
    database_path VARCHAR NOT NULL,
    specification_hashes_json VARCHAR NOT NULL,
    schema_count BIGINT NOT NULL,
    table_count BIGINT NOT NULL,
    view_count BIGINT NOT NULL,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.deployment_run (
    deployment_id VARCHAR PRIMARY KEY,
    release_id VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL,
    source_sha256 VARCHAR,
    working_database_sha256 VARCHAR,
    published_database_sha256 VARCHAR,
    error_class VARCHAR,
    error_message VARCHAR
);

CREATE TABLE IF NOT EXISTS control.source_asset (
    source_asset_id VARCHAR PRIMARY KEY,
    logical_source_name VARCHAR NOT NULL,
    relative_path VARCHAR NOT NULL,
    source_type VARCHAR NOT NULL,
    source_system VARCHAR NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    authoritative_baseline BOOLEAN NOT NULL,
    sha256 VARCHAR NOT NULL,
    size_bytes BIGINT NOT NULL,
    modified_at TIMESTAMP,
    row_count BIGINT NOT NULL,
    column_count BIGINT NOT NULL,
    canonical_schema_hash VARCHAR NOT NULL,
    first_seen_at TIMESTAMP NOT NULL,
    last_seen_at TIMESTAMP NOT NULL,
    UNIQUE(relative_path, sha256)
);

CREATE TABLE IF NOT EXISTS control.source_column (
    source_column_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    column_name VARCHAR NOT NULL,
    ordinal_position BIGINT NOT NULL,
    source_dtype VARCHAR NOT NULL,
    observed_nullable BOOLEAN NOT NULL,
    semantic_role VARCHAR NOT NULL,
    temporal_role VARCHAR NOT NULL,
    provenance_classification VARCHAR NOT NULL,
    UNIQUE(source_asset_id, column_name)
);

CREATE TABLE IF NOT EXISTS control.temporal_contract (
    temporal_contract_id VARCHAR PRIMARY KEY,
    contract_name VARCHAR NOT NULL,
    contract_version VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    required_fields_json VARCHAR NOT NULL,
    prohibited_claims_json VARCHAR NOT NULL,
    eligibility_rule VARCHAR NOT NULL,
    contract_hash VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(contract_name, contract_version)
);

CREATE TABLE IF NOT EXISTS control.snapshot_registry (
    snapshot_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    temporal_contract_id VARCHAR NOT NULL,
    temporal_contract_version VARCHAR NOT NULL,
    source_run_id VARCHAR,
    source_model_version VARCHAR,
    process_timestamp TIMESTAMPTZ,
    observation_date DATE,
    reporting_date DATE,
    origination_date DATE,
    source_date_provenance VARCHAR NOT NULL,
    history_mode VARCHAR NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    identity_grain VARCHAR NOT NULL,
    identity_continuity_status VARCHAR NOT NULL,
    temporal_quality VARCHAR NOT NULL,
    historical_analytics_eligible BOOLEAN NOT NULL,
    snapshot_status VARCHAR NOT NULL,
    population_count BIGINT NOT NULL,
    distinct_entity_count BIGINT NOT NULL,
    timezone VARCHAR,
    limitations VARCHAR NOT NULL,
    registered_at TIMESTAMP NOT NULL,
    validated_at TIMESTAMP,
    published_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS control.snapshot_source_link (
    snapshot_source_link_id VARCHAR PRIMARY KEY,
    snapshot_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    relationship_type VARCHAR NOT NULL,
    source_sha256 VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(snapshot_id, source_asset_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS control.temporal_quality_result (
    quality_result_id VARCHAR PRIMARY KEY,
    deployment_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    rule_name VARCHAR NOT NULL,
    rule_scope VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    actual_value VARCHAR,
    expected_value VARCHAR,
    details VARCHAR,
    checked_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.reconciliation_result (
    reconciliation_id VARCHAR PRIMARY KEY,
    deployment_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    reconciliation_name VARCHAR NOT NULL,
    source_value VARCHAR,
    registry_value VARCHAR,
    difference DOUBLE,
    tolerance DOUBLE NOT NULL,
    status VARCHAR NOT NULL,
    reconciled_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.lineage_node (
    lineage_node_id VARCHAR PRIMARY KEY,
    node_type VARCHAR NOT NULL,
    node_name VARCHAR NOT NULL,
    relative_object_path VARCHAR,
    object_hash VARCHAR,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(node_type, node_name, relative_object_path)
);

CREATE TABLE IF NOT EXISTS control.lineage_edge (
    lineage_edge_id VARCHAR PRIMARY KEY,
    upstream_node_id VARCHAR NOT NULL,
    downstream_node_id VARCHAR NOT NULL,
    transformation_name VARCHAR NOT NULL,
    deployment_id VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.column_lineage (
    column_lineage_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    source_column VARCHAR NOT NULL,
    target_object VARCHAR NOT NULL,
    target_column VARCHAR NOT NULL,
    transformation_type VARCHAR NOT NULL,
    provenance_classification VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.publish_status (
    publish_id VARCHAR PRIMARY KEY,
    deployment_id VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    previous_status VARCHAR,
    new_status VARCHAR NOT NULL,
    transition_at TIMESTAMP NOT NULL,
    details VARCHAR
);

CREATE TABLE IF NOT EXISTS control.rollback_event (
    rollback_id VARCHAR PRIMARY KEY,
    deployment_id VARCHAR NOT NULL,
    database_target VARCHAR NOT NULL,
    backup_path VARCHAR,
    backup_sha256 VARCHAR,
    reason VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    initiated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);
