from __future__ import annotations

from pathlib import Path

from src.temporal_risk.config import (
    BUSINESS_SCHEMAS,
    DDL_FILES,
    EXPECTED_TABLE_COUNT,
    EXPECTED_VIEW_COUNT,
)
from src.temporal_risk.contracts import Phase2AValidationError


def execute_sql_file(connection, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Phase 2A SQL asset not found: {path}")
    connection.execute(path.read_text(encoding="utf-8"))


def initialize_schema(connection) -> None:
    for path in DDL_FILES:
        execute_sql_file(connection, path)


def catalog_signature(connection) -> dict:
    placeholders = ",".join("?" for _ in BUSINESS_SCHEMAS)
    schemas = int(
        connection.execute(
            f"""
            SELECT COUNT(*) FROM information_schema.schemata
            WHERE schema_name IN ({placeholders})
            """,
            list(BUSINESS_SCHEMAS),
        ).fetchone()[0]
    )
    tables = int(
        connection.execute(
            f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema IN ({placeholders})
              AND table_type = 'BASE TABLE'
            """,
            list(BUSINESS_SCHEMAS),
        ).fetchone()[0]
    )
    views = int(
        connection.execute(
            f"""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema IN ({placeholders})
              AND table_type = 'VIEW'
            """,
            list(BUSINESS_SCHEMAS),
        ).fetchone()[0]
    )
    core_objects = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'core'
            """
        ).fetchone()[0]
    )
    mart_objects = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'mart'
            """
        ).fetchone()[0]
    )
    return {
        "schema_count": schemas,
        "table_count": tables,
        "view_count": views,
        "core_object_count": core_objects,
        "mart_object_count": mart_objects,
    }


def validate_catalog(connection) -> dict:
    signature = catalog_signature(connection)
    expected = {
        "schema_count": len(BUSINESS_SCHEMAS),
        "table_count": EXPECTED_TABLE_COUNT,
        "view_count": EXPECTED_VIEW_COUNT,
        "core_object_count": 0,
        "mart_object_count": 0,
    }
    if signature != expected:
        raise Phase2AValidationError(
            f"Phase 2A catalog mismatch: expected {expected}, received {signature}"
        )
    return signature
