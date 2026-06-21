from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from src.enterprise_data.risk_marts.source_catalog import VIEW_DEFINITIONS


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _columns(connection, schema: str, table: str) -> list[str]:
    return [
        str(row[0])
        for row in connection.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
            """,
            [schema, table],
        ).fetchall()
    ]


def build_lineage_manifest(
    connection,
    source_metadata: dict,
    *,
    deployment_timestamp: str | None = None,
) -> dict:
    timestamp = deployment_timestamp or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    view_records = []
    for definition in VIEW_DEFINITIONS:
        source_columns = {}
        for source_object in definition.source_objects:
            schema, table = source_object.split(".", 1)
            source_columns[source_object] = set(
                _columns(connection, schema, table)
            )
        column_records = []
        for target_column in _columns(
            connection,
            "mart",
            definition.view_name,
        ):
            direct_sources = [
                f"{source_object}.{target_column}"
                for source_object, columns in source_columns.items()
                if target_column in columns
            ]
            column_records.append(
                {
                    "target_column": target_column,
                    "source_columns": direct_sources,
                    "transformation": (
                        "DIRECT"
                        if direct_sources
                        else "DERIVED_IN_GOVERNED_SQL_DEFINITION"
                    ),
                }
            )
        view_records.append(
            {
                "target_view": f"mart.{definition.view_name}",
                "source_objects": list(definition.source_objects),
                "sql_file": definition.sql_path.relative_to(
                    definition.sql_path.parents[2]
                ).as_posix(),
                "sql_sha256": _sha256(definition.sql_path),
                "column_lineage": column_records,
            }
        )
    return {
        "framework": "KRONOS Phase 4D Enterprise Risk Marts",
        "deployment_timestamp": timestamp,
        "source_asset_id": source_metadata["source_asset_id"],
        "source_hash": source_metadata["source_hash"],
        "source_run_id": source_metadata["source_run_id"],
        "model_version": source_metadata["model_version"],
        "published_batch_id": source_metadata["published_batch_id"],
        "warehouse_lineage_tables_modified": False,
        "views": view_records,
    }
