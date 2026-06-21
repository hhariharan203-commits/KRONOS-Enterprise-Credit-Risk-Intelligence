from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now


def build_lineage(
    connection,
    *,
    readiness_run_id: str,
    source_context: dict,
    readiness_contract: dict,
    domain_contract: dict,
) -> dict:
    earlier = source_context["earlier"]
    later = source_context["later"]
    nodes = (
        ("READINESS_CONTRACT", readiness_contract["contract_name"], readiness_contract["contract_id"], readiness_contract["contract_hash"]),
        ("STATE_DOMAIN_CONTRACT", domain_contract["contract_name"], domain_contract["contract_id"], domain_contract["contract_hash"]),
        ("EARLIER_SNAPSHOT", earlier["snapshot_id"], earlier["snapshot_id"], earlier["source_sha256"]),
        ("LATER_SNAPSHOT", later["snapshot_id"], later["snapshot_id"], later["source_sha256"]),
        ("EARLIER_IDENTITY_MAPPING", earlier["identity_source_column"], earlier["ingestion_batch_id"], earlier["source_sha256"]),
        ("LATER_IDENTITY_MAPPING", later["identity_source_column"], later["ingestion_batch_id"], later["source_sha256"]),
        ("EARLIER_STATE_MAPPING", earlier["state_source_column"], earlier["ingestion_batch_id"], earlier["source_sha256"]),
        ("LATER_STATE_MAPPING", later["state_source_column"], later["ingestion_batch_id"], later["source_sha256"]),
        ("CONTINUITY_CONTROL_EVIDENCE", readiness_run_id, readiness_run_id, stable_id(readiness_run_id, "CONTROL_EVIDENCE")),
        ("PUBLISHED_READINESS_RUN", readiness_run_id, readiness_run_id, stable_id(readiness_run_id, "PUBLISHED")),
    )
    node_ids = {}
    now = utc_now()
    for node_type, node_name, identifier, object_hash in nodes:
        node_id = stable_id(readiness_run_id, node_type, node_name)
        node_ids[node_type] = node_id
        connection.execute(
            """
            INSERT INTO control.migration_lineage_node (
                lineage_node_id, readiness_run_id, node_type, node_name,
                governed_object_identifier, object_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                node_id,
                readiness_run_id,
                node_type,
                node_name,
                identifier,
                object_hash,
                now,
            ],
        )
    edges = (
        ("READINESS_CONTRACT", "CONTINUITY_CONTROL_EVIDENCE", "GOVERNS_CONTROL_EVIDENCE"),
        ("STATE_DOMAIN_CONTRACT", "EARLIER_STATE_MAPPING", "GOVERNS_STATE_VALIDATION"),
        ("STATE_DOMAIN_CONTRACT", "LATER_STATE_MAPPING", "GOVERNS_STATE_VALIDATION"),
        ("EARLIER_SNAPSHOT", "EARLIER_IDENTITY_MAPPING", "SUPPLIES_IDENTITY_MAPPING"),
        ("LATER_SNAPSHOT", "LATER_IDENTITY_MAPPING", "SUPPLIES_IDENTITY_MAPPING"),
        ("EARLIER_SNAPSHOT", "EARLIER_STATE_MAPPING", "SUPPLIES_STATE_MAPPING"),
        ("LATER_SNAPSHOT", "LATER_STATE_MAPPING", "SUPPLIES_STATE_MAPPING"),
        ("EARLIER_IDENTITY_MAPPING", "CONTINUITY_CONTROL_EVIDENCE", "SUPPORTS_CONTINUITY_VALIDATION"),
        ("LATER_IDENTITY_MAPPING", "CONTINUITY_CONTROL_EVIDENCE", "SUPPORTS_CONTINUITY_VALIDATION"),
        ("EARLIER_STATE_MAPPING", "CONTINUITY_CONTROL_EVIDENCE", "SUPPORTS_DOMAIN_VALIDATION"),
        ("LATER_STATE_MAPPING", "CONTINUITY_CONTROL_EVIDENCE", "SUPPORTS_DOMAIN_VALIDATION"),
        ("CONTINUITY_CONTROL_EVIDENCE", "PUBLISHED_READINESS_RUN", "AUTHORIZES_GOVERNED_PUBLICATION"),
    )
    for upstream, downstream, relationship in edges:
        connection.execute(
            """
            INSERT INTO control.migration_lineage_edge (
                lineage_edge_id, readiness_run_id, upstream_node_id,
                downstream_node_id, governance_relationship, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                stable_id(
                    readiness_run_id,
                    node_ids[upstream],
                    node_ids[downstream],
                    relationship,
                ),
                readiness_run_id,
                node_ids[upstream],
                node_ids[downstream],
                relationship,
                now,
            ],
        )
    column_rows = (
        (earlier, earlier["identity_source_column"], "source_facility_id" if earlier["identity_grain"] == "FACILITY" else "source_entity_id", "IDENTITY_CONTINUITY"),
        (later, later["identity_source_column"], "source_facility_id" if later["identity_grain"] == "FACILITY" else "source_entity_id", "IDENTITY_CONTINUITY"),
        (earlier, earlier["date_source_column"], earlier["date_canonical_field"], "SNAPSHOT_CONTINUITY"),
        (later, later["date_source_column"], later["date_canonical_field"], "SNAPSHOT_CONTINUITY"),
        (earlier, earlier["state_source_column"], source_context["state_field"], "STATE_FIELD_CONTINUITY"),
        (later, later["state_source_column"], source_context["state_field"], "STATE_FIELD_CONTINUITY"),
    )
    for snapshot, source_column, canonical_field, target in column_rows:
        connection.execute(
            """
            INSERT INTO control.migration_column_lineage (
                column_lineage_id, readiness_run_id, snapshot_id,
                source_asset_id, source_column, canonical_field,
                governance_target, transformation_type,
                provenance_classification, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'SOURCE_MAPPING_REFERENCE',
                      'SOURCE_SUPPLIED', ?)
            """,
            [
                stable_id(
                    readiness_run_id,
                    snapshot["snapshot_id"],
                    source_column,
                    canonical_field,
                    target,
                ),
                readiness_run_id,
                snapshot["snapshot_id"],
                snapshot["source_asset_id"],
                source_column,
                canonical_field,
                target,
                now,
            ],
        )
    counts = {
        "node_count": connection.execute(
            "SELECT COUNT(*) FROM control.migration_lineage_node WHERE readiness_run_id = ?",
            [readiness_run_id],
        ).fetchone()[0],
        "edge_count": connection.execute(
            "SELECT COUNT(*) FROM control.migration_lineage_edge WHERE readiness_run_id = ?",
            [readiness_run_id],
        ).fetchone()[0],
        "column_lineage_count": connection.execute(
            "SELECT COUNT(*) FROM control.migration_column_lineage WHERE readiness_run_id = ?",
            [readiness_run_id],
        ).fetchone()[0],
    }
    counts["complete"] = (
        counts["node_count"] == 10
        and counts["edge_count"] == 12
        and counts["column_lineage_count"] >= 6
    )
    return counts
