CREATE TABLE IF NOT EXISTS control.migration_lineage_node (
    lineage_node_id VARCHAR PRIMARY KEY,
    readiness_run_id VARCHAR NOT NULL,
    node_type VARCHAR NOT NULL,
    node_name VARCHAR NOT NULL,
    governed_object_identifier VARCHAR,
    object_hash VARCHAR,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(readiness_run_id, node_type, node_name)
);

CREATE TABLE IF NOT EXISTS control.migration_lineage_edge (
    lineage_edge_id VARCHAR PRIMARY KEY,
    readiness_run_id VARCHAR NOT NULL,
    upstream_node_id VARCHAR NOT NULL,
    downstream_node_id VARCHAR NOT NULL,
    governance_relationship VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(
        readiness_run_id,
        upstream_node_id,
        downstream_node_id,
        governance_relationship
    )
);

CREATE TABLE IF NOT EXISTS control.migration_column_lineage (
    column_lineage_id VARCHAR PRIMARY KEY,
    readiness_run_id VARCHAR NOT NULL,
    snapshot_id VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    source_column VARCHAR NOT NULL,
    canonical_field VARCHAR NOT NULL,
    governance_target VARCHAR NOT NULL,
    transformation_type VARCHAR NOT NULL,
    provenance_classification VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE(
        readiness_run_id,
        snapshot_id,
        source_column,
        canonical_field,
        governance_target
    )
);
