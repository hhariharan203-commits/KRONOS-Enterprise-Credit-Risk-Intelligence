from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now


def build_lineage(
    connection,
    *,
    ingestion_batch_id: str,
    source_asset_id: str,
    source_hash: str,
    manifest: dict,
    contract_id: str,
    contract_hash: str,
    snapshot_id: str,
    mappings: list[dict],
) -> dict:
    now = utc_now()
    nodes = [
        ("MANIFEST", manifest["manifest_relative_path"], manifest["manifest_relative_path"], manifest["manifest_sha256"]),
        ("SOURCE", manifest["source_relative_path"], manifest["source_relative_path"], source_hash),
        ("TEMPORAL_CONTRACT", contract_id, "control.temporal_contract", contract_hash),
        ("FIELD_MAPPING", ingestion_batch_id, "control.historical_field_mapping", stable_id(ingestion_batch_id, "MAPPINGS")),
        ("SNAPSHOT_STAGING", snapshot_id, "staging.stg_historical_snapshot_row", source_hash),
        ("EVENT_STAGING", snapshot_id, "staging.stg_historical_event_row", source_hash),
        ("ENTITY_DIMENSION", snapshot_id, "core.dim_historical_entity", source_hash),
        ("FACILITY_DIMENSION", snapshot_id, "core.dim_historical_facility", source_hash),
        ("SNAPSHOT_DIMENSION", snapshot_id, "core.dim_historical_snapshot", source_hash),
        ("OBSERVATION_FACT", snapshot_id, "core.fact_historical_credit_observation", source_hash),
        ("EVENT_FACT", snapshot_id, "core.fact_historical_credit_event", source_hash),
        ("READINESS", snapshot_id, "control.data_readiness_result", source_hash),
        ("REJECTS", snapshot_id, "control.historical_reject_record", source_hash),
        ("PUBLISHED_BATCH", ingestion_batch_id, "control.historical_ingestion_batch", source_hash),
    ]
    node_ids = {}
    for node_type, name, path, object_hash in nodes:
        node_id = stable_id(ingestion_batch_id, node_type, name, path)
        node_ids[node_type] = node_id
        connection.execute(
            """
            INSERT INTO control.historical_lineage_node (
                historical_lineage_node_id, ingestion_batch_id, node_type,
                node_name, relative_object_path, object_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [node_id, ingestion_batch_id, node_type, name, path, object_hash, now],
        )
    edges = (
        ("MANIFEST", "SOURCE", "MANIFEST_DECLARES_SOURCE"),
        ("TEMPORAL_CONTRACT", "FIELD_MAPPING", "CONTRACT_GOVERNS_MAPPING"),
        ("SOURCE", "SNAPSHOT_STAGING", "IMMUTABLE_EXTRACTION"),
        ("SOURCE", "EVENT_STAGING", "SOURCE_EVENT_NORMALIZATION"),
        ("FIELD_MAPPING", "SNAPSHOT_STAGING", "EXPLICIT_MAPPING"),
        ("SNAPSHOT_STAGING", "ENTITY_DIMENSION", "WAREHOUSE_KEY_HASHING"),
        ("SNAPSHOT_STAGING", "FACILITY_DIMENSION", "WAREHOUSE_KEY_HASHING"),
        ("SNAPSHOT_STAGING", "SNAPSHOT_DIMENSION", "SNAPSHOT_REGISTRATION"),
        ("SNAPSHOT_STAGING", "OBSERVATION_FACT", "SAFE_CAST_AND_NULL_PRESERVATION"),
        ("EVENT_STAGING", "EVENT_FACT", "SOURCE_EVENT_NORMALIZATION"),
        ("OBSERVATION_FACT", "READINESS", "INPUT_AVAILABILITY_ASSESSMENT"),
        ("SNAPSHOT_STAGING", "REJECTS", "ROW_QUALITY_CLASSIFICATION"),
        ("READINESS", "PUBLISHED_BATCH", "CONTROLLED_PUBLICATION"),
    )
    for upstream, downstream, transformation in edges:
        edge_id = stable_id(
            ingestion_batch_id,
            node_ids[upstream],
            node_ids[downstream],
            transformation,
        )
        connection.execute(
            """
            INSERT INTO control.historical_lineage_edge (
                historical_lineage_edge_id, ingestion_batch_id,
                upstream_node_id, downstream_node_id, transformation_name,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                edge_id,
                ingestion_batch_id,
                node_ids[upstream],
                node_ids[downstream],
                transformation,
                now,
            ],
        )
    for mapping in mappings:
        target_object = "core.fact_historical_credit_observation"
        target_column = mapping["canonical_column"]
        lineage_id = stable_id(
            ingestion_batch_id,
            source_asset_id,
            mapping["source_column"],
            target_object,
            target_column,
        )
        connection.execute(
            """
            INSERT INTO control.historical_column_lineage (
                historical_column_lineage_id, ingestion_batch_id,
                source_asset_id, source_column, target_object, target_column,
                transformation_type, provenance_classification, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'SOURCE_SUPPLIED', ?)
            """,
            [
                lineage_id,
                ingestion_batch_id,
                source_asset_id,
                mapping["source_column"],
                target_object,
                target_column,
                "EXPLICIT_RENAME_SAFE_CAST",
                now,
            ],
        )
    counts = {
        "node_count": connection.execute(
            "SELECT COUNT(*) FROM control.historical_lineage_node WHERE ingestion_batch_id = ?",
            [ingestion_batch_id],
        ).fetchone()[0],
        "edge_count": connection.execute(
            "SELECT COUNT(*) FROM control.historical_lineage_edge WHERE ingestion_batch_id = ?",
            [ingestion_batch_id],
        ).fetchone()[0],
        "column_lineage_count": connection.execute(
            "SELECT COUNT(*) FROM control.historical_column_lineage WHERE ingestion_batch_id = ?",
            [ingestion_batch_id],
        ).fetchone()[0],
    }
    counts["complete"] = (
        counts["node_count"] == len(nodes)
        and counts["edge_count"] == len(edges)
        and counts["column_lineage_count"] == len(mappings)
    )
    return counts
