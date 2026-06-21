from __future__ import annotations

import json

from src.temporal_risk.audit import stable_id, utc_now


def _record(
    connection,
    *,
    deployment_id: str,
    snapshot_id: str,
    source_asset_id: str,
    name: str,
    source_value,
    registry_value,
) -> dict:
    equal = str(source_value) == str(registry_value)
    result_id = stable_id(deployment_id, snapshot_id, name)
    connection.execute(
        """
        INSERT INTO control.reconciliation_result (
            reconciliation_id, deployment_id, snapshot_id, source_asset_id,
            reconciliation_name, source_value, registry_value, difference,
            tolerance, status, reconciled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """,
        [
            result_id,
            deployment_id,
            snapshot_id,
            source_asset_id,
            name,
            str(source_value),
            str(registry_value),
            0.0 if equal else 1.0,
            "PASS" if equal else "FAIL",
            utc_now(),
        ],
    )
    return {"name": name, "status": "PASS" if equal else "FAIL"}


def run_reconciliations(
    connection,
    *,
    deployment_id: str,
    snapshot_id: str,
    source_asset_id: str,
    profile: dict,
    baseline_profile: dict,
) -> dict:
    registry = connection.execute(
        """
        SELECT population_count, distinct_entity_count, source_run_id,
               source_model_version
        FROM control.snapshot_registry
        WHERE snapshot_id = ?
        """,
        [snapshot_id],
    ).fetchone()
    source = connection.execute(
        """
        SELECT column_count, canonical_schema_hash, sha256
        FROM control.source_asset WHERE source_asset_id = ?
        """,
        [source_asset_id],
    ).fetchone()
    column_registry_count = connection.execute(
        "SELECT COUNT(*) FROM control.source_column WHERE source_asset_id = ?",
        [source_asset_id],
    ).fetchone()[0]
    link_hash = connection.execute(
        """
        SELECT source_sha256 FROM control.snapshot_source_link
        WHERE snapshot_id = ? AND source_asset_id = ?
        """,
        [snapshot_id, source_asset_id],
    ).fetchone()[0]
    values = (
        ("source_rows_to_snapshot_population", profile["row_count"], registry[0]),
        ("source_columns_to_column_registry", profile["column_count"], column_registry_count),
        ("source_rows_to_distinct_borrowers", profile["row_count"], profile["distinct_borrower_count"]),
        (
            "run_id_inventory_to_baseline",
            json.dumps(sorted(profile["run_ids"])),
            json.dumps(sorted(baseline_profile["run_ids"])),
        ),
        (
            "model_version_inventory_to_baseline",
            json.dumps(sorted(profile["model_versions"])),
            json.dumps(sorted(baseline_profile["model_versions"])),
        ),
        ("source_hash_to_snapshot_link", profile["sha256_before"], link_hash),
        ("timestamp_count_to_registry", len(profile["timestamps"]), 1),
        ("source_schema_hash_to_registry", profile["canonical_schema_hash"], source[1]),
        ("successful_scoring_rows_to_population", profile["scoring_status"].get("SCORED", 0), registry[0]),
    )
    results = [
        _record(
            connection,
            deployment_id=deployment_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            name=name,
            source_value=source_value,
            registry_value=registry_value,
        )
        for name, source_value, registry_value in values
    ]
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL",
        "reconciliation_count": len(results),
        "failure_count": sum(item["status"] == "FAIL" for item in results),
        "results": results,
    }
