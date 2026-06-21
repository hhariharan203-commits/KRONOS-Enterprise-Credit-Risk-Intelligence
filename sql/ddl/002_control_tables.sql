CREATE TABLE IF NOT EXISTS control.etl_batch (
    etl_batch_id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL,
    warehouse_version VARCHAR NOT NULL,
    source_count BIGINT DEFAULT 0,
    loaded_source_count BIGINT DEFAULT 0,
    skipped_source_count BIGINT DEFAULT 0,
    error_message VARCHAR
);

CREATE TABLE IF NOT EXISTS control.etl_step_run (
    step_run_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    step_name VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR NOT NULL,
    row_count BIGINT,
    message VARCHAR
);

CREATE TABLE IF NOT EXISTS control.source_asset (
    source_asset_id VARCHAR PRIMARY KEY,
    source_name VARCHAR NOT NULL,
    source_domain VARCHAR NOT NULL,
    relative_path VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    sha256 VARCHAR NOT NULL,
    size_bytes BIGINT NOT NULL,
    modified_at TIMESTAMP,
    row_count BIGINT,
    schema_json VARCHAR,
    first_seen_at TIMESTAMP NOT NULL,
    last_seen_at TIMESTAMP NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(relative_path, sha256)
);

CREATE TABLE IF NOT EXISTS control.artifact_registry (
    artifact_id VARCHAR PRIMARY KEY,
    relative_path VARCHAR NOT NULL,
    artifact_type VARCHAR NOT NULL,
    content_class VARCHAR NOT NULL,
    sha256 VARCHAR NOT NULL,
    size_bytes BIGINT NOT NULL,
    modified_at TIMESTAMP,
    registered_at TIMESTAMP NOT NULL,
    binary_stored BOOLEAN NOT NULL DEFAULT FALSE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(relative_path, sha256)
);

CREATE TABLE IF NOT EXISTS control.schema_snapshot (
    schema_snapshot_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    column_name VARCHAR NOT NULL,
    ordinal_position BIGINT NOT NULL,
    source_dtype VARCHAR,
    nullable BOOLEAN,
    captured_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.data_quality_result (
    quality_result_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    check_name VARCHAR NOT NULL,
    check_scope VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    actual_value VARCHAR,
    expected_value VARCHAR,
    details VARCHAR,
    checked_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.reconciliation_result (
    reconciliation_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    reconciliation_name VARCHAR NOT NULL,
    source_value DOUBLE,
    warehouse_value DOUBLE,
    absolute_difference DOUBLE,
    tolerance DOUBLE NOT NULL,
    status VARCHAR NOT NULL,
    reconciled_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.rejected_record (
    rejected_record_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    source_row_number BIGINT,
    rejection_reason VARCHAR NOT NULL,
    payload_json VARCHAR,
    rejected_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.publish_status (
    publish_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    target_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    row_count BIGINT,
    published_at TIMESTAMP NOT NULL,
    details VARCHAR
);

CREATE TABLE IF NOT EXISTS control.lineage_node (
    lineage_node_id VARCHAR PRIMARY KEY,
    node_type VARCHAR NOT NULL,
    node_name VARCHAR NOT NULL,
    object_path VARCHAR,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(node_type, node_name, object_path)
);

CREATE TABLE IF NOT EXISTS control.lineage_edge (
    lineage_edge_id VARCHAR PRIMARY KEY,
    upstream_node_id VARCHAR NOT NULL,
    downstream_node_id VARCHAR NOT NULL,
    transformation_name VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS control.column_lineage (
    column_lineage_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    source_column VARCHAR NOT NULL,
    target_schema VARCHAR NOT NULL,
    target_table VARCHAR NOT NULL,
    target_column VARCHAR NOT NULL,
    transformation VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL
);
