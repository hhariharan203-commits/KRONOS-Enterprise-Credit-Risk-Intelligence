from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.historical_ingestion.pipeline import (
    deploy_phase2b_schema,
    validate_phase2b_catalog,
)
from test_phase2b_contracts import deployed_phase2b, seed_phase2a_database


def test_phase2b_exact_catalog() -> None:
    _, database = deployed_phase2b()
    connection = connect_temporal(database)
    try:
        catalog = validate_phase2b_catalog(connection)
        assert (catalog["schema_count"], catalog["table_count"], catalog["view_count"]) == (
            5,
            36,
            0,
        )
        assert catalog["mart_object_count"] == 0
    finally:
        connection.close()


def test_schema_deployment_ignores_stale_working_and_wal_files(tmp_path) -> None:
    root = tmp_path / "temporal_platform"
    database = seed_phase2a_database(root)
    stale = database.parent / ".phase2a-stale.working.duckdb"
    stale_wal = database.parent / ".phase2a-stale.working.duckdb.wal"
    stale.write_bytes(b"not-a-database")
    stale_wal.write_bytes(b"stale-wal")
    result = deploy_phase2b_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2B_SCHEMA_READY"
    assert stale.read_bytes() == b"not-a-database"
    assert stale_wal.read_bytes() == b"stale-wal"
