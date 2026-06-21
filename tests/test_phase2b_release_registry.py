from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.historical_ingestion.pipeline import (
    deploy_phase2b_schema,
    phase2a_row_inventory,
)
from test_phase2b_contracts import deployed_phase2b, seed_phase2a_database


def test_phase2b_release_is_distinct_and_phase2a_release_is_preserved() -> None:
    _, database = deployed_phase2b()
    connection = connect_temporal(database)
    try:
        rows = connection.execute(
            "SELECT phase_name, table_count, view_count FROM control.platform_release ORDER BY phase_name"
        ).fetchall()
        assert rows == [("PHASE2A", 17, 0), ("PHASE2B", 36, 0)]
    finally:
        connection.close()


def test_original_phase2a_rows_are_unchanged_by_pk_and_hash(tmp_path) -> None:
    root = tmp_path / "temporal_platform"
    database = seed_phase2a_database(root)
    before_connection = connect_temporal(database)
    try:
        before = phase2a_row_inventory(before_connection)
    finally:
        before_connection.close()
    deploy_phase2b_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    after_connection = connect_temporal(database)
    try:
        after = phase2a_row_inventory(after_connection)
    finally:
        after_connection.close()
    for table, records in before.items():
        for key, digest in records["rows"].items():
            assert after[table]["rows"][key] == digest
