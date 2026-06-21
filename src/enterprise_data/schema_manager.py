from __future__ import annotations

from pathlib import Path

from src.enterprise_data.config import SCHEMA_SQL_FILES


def execute_sql_file(connection, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Warehouse SQL asset not found: {path}")
    connection.execute(path.read_text(encoding="utf-8"))


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
