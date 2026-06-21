from __future__ import annotations

from pathlib import Path

from src.enterprise_data.config import (
    CONTROL_VIEW_SQL_FILES,
    SCHEMA_SQL_FILES,
)


RECONCILIATION_RESULT_MIGRATIONS = (
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS job_id VARCHAR",
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS source_count BIGINT",
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS staging_count BIGINT",
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS core_count BIGINT",
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS mart_count BIGINT",
    "ALTER TABLE control.reconciliation_result "
    "ADD COLUMN IF NOT EXISTS variance DOUBLE",
)


def execute_sql_file(connection, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Warehouse SQL asset not found: {path}")
    connection.execute(path.read_text(encoding="utf-8"))


def ensure_reconciliation_result_schema(connection) -> None:
    for statement in RECONCILIATION_RESULT_MIGRATIONS:
        connection.execute(statement)


def refresh_control_views(connection) -> None:
    for path in CONTROL_VIEW_SQL_FILES:
        execute_sql_file(connection, path)


def initialize_warehouse(connection) -> None:
    for path in SCHEMA_SQL_FILES:
        execute_sql_file(connection, path)
    connection.execute(
        """
        ALTER TABLE control.source_asset
        ADD COLUMN IF NOT EXISTS is_current BOOLEAN DEFAULT TRUE
        """
    )
    connection.execute(
        """
        ALTER TABLE control.artifact_registry
        ADD COLUMN IF NOT EXISTS is_current BOOLEAN DEFAULT TRUE
        """
    )
    ensure_reconciliation_result_schema(connection)
    refresh_control_views(connection)


def table_exists(connection, schema_name: str, table_name: str) -> bool:
    return bool(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = ? AND table_name = ?
            """,
            [schema_name, table_name],
        ).fetchone()[0]
    )


def table_columns(connection, schema_name: str, table_name: str) -> list[str]:
    rows = connection.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = ? AND table_name = ?
        ORDER BY ordinal_position
        """,
        [schema_name, table_name],
    ).fetchall()
    return [row[0] for row in rows]
