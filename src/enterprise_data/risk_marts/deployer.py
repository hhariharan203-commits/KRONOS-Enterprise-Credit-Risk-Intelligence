from __future__ import annotations

from pathlib import Path

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import (
    connect_warehouse,
    discard_working_database,
    prepare_working_database,
    publish_working_database,
)
from src.enterprise_data.risk_marts.lineage_manifest import (
    build_lineage_manifest,
)
from src.enterprise_data.risk_marts.reconciliation import reconcile_phase4d
from src.enterprise_data.risk_marts.source_catalog import (
    VIEW_DEFINITIONS,
    existing_mart_row_counts,
    source_context,
    warehouse_inventory,
)
from src.enterprise_data.risk_marts.validator import validate_phase4d


def _execute_sql_file(connection, path: Path) -> None:
    connection.execute(path.read_text(encoding="utf-8"))


def deploy_phase4d_views(
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    working_database = prepare_working_database(database_path)
    connection = None
    result = None
    try:
        connection = connect_warehouse(working_database.working_path)
        before_inventory = warehouse_inventory(connection)
        before_marts = existing_mart_row_counts(connection)
        metadata = source_context(connection)

        for definition in VIEW_DEFINITIONS:
            _execute_sql_file(connection, definition.sql_path)

        validation = validate_phase4d(
            connection,
            expected_existing_mart_rows=before_marts,
        )
        reconciliation = reconcile_phase4d(connection)
        lineage = build_lineage_manifest(connection, metadata)
        after_inventory = warehouse_inventory(connection)
        after_marts = existing_mart_row_counts(connection)

        if before_inventory["schema_count"] != after_inventory["schema_count"]:
            raise RuntimeError("Phase 4D changed the warehouse schema count.")
        if before_inventory["table_count"] != after_inventory["table_count"]:
            raise RuntimeError("Phase 4D changed the warehouse table count.")
        if before_marts != after_marts:
            raise RuntimeError("Phase 4D changed an existing mart row count.")

        result = {
            "before_inventory": before_inventory,
            "after_inventory": after_inventory,
            "existing_mart_row_counts_before": before_marts,
            "existing_mart_row_counts_after": after_marts,
            "views_deployed": [
                f"mart.{definition.view_name}"
                for definition in VIEW_DEFINITIONS
            ],
            "source_metadata": metadata,
            "validation": validation,
            "reconciliation": reconciliation,
            "lineage_manifest": lineage,
        }
    finally:
        if connection is not None:
            connection.close()
        if result is not None:
            publish_working_database(working_database)
        discard_working_database(working_database)
    return result
