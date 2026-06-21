from __future__ import annotations

from pathlib import Path

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.schema_manager import initialize_schema, validate_catalog


def test_phase2a_exact_catalog(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    database = root / "warehouse" / "phase2a.duckdb"
    connection = connect_temporal(
        database,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    try:
        initialize_schema(connection)
        assert validate_catalog(connection) == {
            "schema_count": 5,
            "table_count": 17,
            "view_count": 0,
            "core_object_count": 0,
            "mart_object_count": 0,
        }
    finally:
        connection.close()
