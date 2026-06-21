from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now


def build_lineage(
    connection,
    *,
    deployment_id: str,
    source_asset_id: str,
    source_hash: str,
    contract: dict,
    snapshot_id: str,
    release_id: str,
) -> dict:
    now = utc_now()
    nodes = (
        ("SOURCE_ASSET", "scored_portfolio", "data/processed/scored_portfolio.csv", source_hash),
        ("TEMPORAL_CONTRACT", "CURRENT_STATE_BASELINE_V1", "control.temporal_contract", contract["contract_hash"]),
        ("SNAPSHOT_MANIFEST", snapshot_id, "staging.stg_snapshot_manifest", source_hash),
        ("SNAPSHOT_REGISTRY", snapshot_id, "control.snapshot_registry", source_hash),
        ("PUBLISHED_RELEASE", release_id, "control.platform_release", release_id),
    )
    node_ids = {}
    for node_type, name, path, object_hash in nodes:
        node_id = stable_id(node_type, name, path)
        node_ids[node_type] = node_id
        connection.execute(
            """
            INSERT OR IGNORE INTO control.lineage_node (
                lineage_node_id, node_type, node_name,
                relative_object_path, object_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [node_id, node_type, name, path, object_hash, now],
        )
    edges = (
        ("SOURCE_ASSET", "SNAPSHOT_MANIFEST", "METADATA_DISCOVERY"),
        ("TEMPORAL_CONTRACT", "SNAPSHOT_MANIFEST", "CONTRACT_GOVERNS"),
        ("SNAPSHOT_MANIFEST", "SNAPSHOT_REGISTRY", "TEMPORAL_REGISTRATION"),
        ("SNAPSHOT_REGISTRY", "PUBLISHED_RELEASE", "CONTROL_PUBLICATION"),
    )
    for upstream, downstream, transformation in edges:
        edge_id = stable_id(node_ids[upstream], node_ids[downstream], transformation)
        connection.execute(
            """
            INSERT OR IGNORE INTO control.lineage_edge (
                lineage_edge_id, upstream_node_id, downstream_node_id,
                transformation_name, deployment_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                edge_id,
                node_ids[upstream],
                node_ids[downstream],
                transformation,
                deployment_id,
                now,
            ],
        )
    columns = (
        ("timestamp", "control.snapshot_registry", "process_timestamp", "IDENTITY_NORMALIZATION"),
        ("run_id", "control.snapshot_registry", "source_run_id", "IDENTITY_NORMALIZATION"),
        ("model_version", "control.snapshot_registry", "source_model_version", "IDENTITY_NORMALIZATION"),
        ("borrower_id", "control.snapshot_registry", "distinct_entity_count", "COUNT_DISTINCT_AGGREGATION"),
    )
    for source_column, target, target_column, transformation in columns:
        lineage_id = stable_id(
            source_asset_id,
            source_column,
            target,
            target_column,
            transformation,
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO control.column_lineage (
                column_lineage_id, source_asset_id, source_column,
                target_object, target_column, transformation_type,
                provenance_classification, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'SOURCE_DERIVED_METADATA', ?)
            """,
            [
                lineage_id,
                source_asset_id,
                source_column,
                target,
                target_column,
                transformation,
                now,
            ],
        )
    counts = {
        "node_count": int(connection.execute("SELECT COUNT(*) FROM control.lineage_node").fetchone()[0]),
        "edge_count": int(connection.execute("SELECT COUNT(*) FROM control.lineage_edge").fetchone()[0]),
        "column_lineage_count": int(connection.execute("SELECT COUNT(*) FROM control.column_lineage").fetchone()[0]),
    }
    counts["complete"] = counts == {
        "node_count": 5,
        "edge_count": 4,
        "column_lineage_count": 4,
    }
    return counts
