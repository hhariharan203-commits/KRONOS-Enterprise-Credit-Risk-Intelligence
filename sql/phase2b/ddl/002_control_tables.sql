CREATE TABLE IF NOT EXISTS control.historical_ingestion_batch (
    ingestion_batch_id VARCHAR PRIMARY KEY,
    release_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    manifest_asset_id VARCHAR,
    temporal_contract_id VARCHAR,
    temporal_contract_version VARCHAR,
    history_mode VARCHAR,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL,
    records_read BIGINT NOT NULL DEFAULT 0,
    records_staged BIGINT NOT NULL DEFAULT 0,
    records_accepted BIGINT NOT NULL DEFAULT 0,
    records_rejected BIGINT NOT NULL DEFAULT 0,
    records_inserted BIGINT NOT NULL DEFAULT 0,
    records_skipped BIGINT NOT NULL DEFAULT 0,
    snapshot_count BIGINT NOT NULL DEFAULT 0,
    source_sha256 VARCHAR,
    manifest_sha256 VARCHAR,
    working_database_sha256 VARCHAR,
    published_database_sha256 VARCHAR,
    quality_score DOUBLE,
    quality_status VARCHAR,
    quality_details_json VARCHAR,
    error_class VARCHAR,
    error_message VARCHAR
);

CREATE TABLE IF NOT EXISTS control.historical_ingestion_file (
    ingestion_file_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    manifest_asset_id VARCHAR NOT NULL,
    source_relative_path VARCHAR NOT NULL,
    manifest_relative_path VARCHAR NOT NULL,
    source_format VARCHAR NOT NULL,
    source_sha256 VARCHAR NOT NULL,
    manifest_sha256 VARCHAR NOT NULL,
    canonical_schema_hash VARCHAR NOT NULL,
    row_count BIGINT NOT NULL,
    column_count BIGINT NOT NULL,
    declared_snapshot_date DATE NOT NULL,
    observed_snapshot_date DATE NOT NULL,
    status VARCHAR NOT NULL,
    registered_at TIMESTAMP NOT NULL,
    validated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS control.historical_field_mapping (
    field_mapping_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    source_column VARCHAR NOT NULL,
    canonical_column VARCHAR NOT NULL,
    mapping_type VARCHAR NOT NULL,
    required_flag BOOLEAN NOT NULL,
    source_supplied_flag BOOLEAN NOT NULL,
    allowed_cast VARCHAR,
    transformation_description VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, canonical_column)
);

CREATE TABLE IF NOT EXISTS control.historical_reject_record (
    reject_record_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    source_row_number BIGINT NOT NULL,
    raw_entity_identifier VARCHAR,
    raw_facility_identifier VARCHAR,
    column_name VARCHAR,
    invalid_value VARCHAR,
    severity VARCHAR NOT NULL,
    rejection_reason VARCHAR NOT NULL,
    source_payload_json VARCHAR NOT NULL,
    rejected_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.data_readiness_result (
    readiness_result_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    capability_name VARCHAR NOT NULL,
    data_status VARCHAR NOT NULL,
    activation_status VARCHAR NOT NULL,
    required_fields_json VARCHAR NOT NULL,
    available_fields_json VARCHAR NOT NULL,
    missing_fields_json VARCHAR NOT NULL,
    history_mode VARCHAR NOT NULL,
    evidence_classification VARCHAR NOT NULL,
    reason VARCHAR NOT NULL,
    evaluated_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, snapshot_id, capability_name)
);

CREATE TABLE IF NOT EXISTS control.historical_reconciliation_result (
    historical_reconciliation_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    reconciliation_name VARCHAR NOT NULL,
    source_value VARCHAR,
    target_value VARCHAR,
    difference DOUBLE,
    tolerance DOUBLE NOT NULL,
    status VARCHAR NOT NULL,
    details VARCHAR,
    reconciled_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, snapshot_id, reconciliation_name)
);

CREATE TABLE IF NOT EXISTS control.historical_lineage_node (
    historical_lineage_node_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    node_type VARCHAR NOT NULL,
    node_name VARCHAR NOT NULL,
    relative_object_path VARCHAR,
    object_hash VARCHAR,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, node_type, node_name, relative_object_path)
);

CREATE TABLE IF NOT EXISTS control.historical_lineage_edge (
    historical_lineage_edge_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    upstream_node_id VARCHAR NOT NULL,
    downstream_node_id VARCHAR NOT NULL,
    transformation_name VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, upstream_node_id, downstream_node_id, transformation_name)
);

CREATE TABLE IF NOT EXISTS control.historical_column_lineage (
    historical_column_lineage_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    source_column VARCHAR NOT NULL,
    target_object VARCHAR NOT NULL,
    target_column VARCHAR NOT NULL,
    transformation_type VARCHAR NOT NULL,
    provenance_classification VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(ingestion_batch_id, source_column, target_object, target_column)
);

CREATE TABLE IF NOT EXISTS control.historical_publish_status (
    historical_publish_id VARCHAR PRIMARY KEY,
    ingestion_batch_id VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    previous_status VARCHAR,
    new_status VARCHAR NOT NULL,
    transition_at TIMESTAMP NOT NULL,
    details VARCHAR
);
