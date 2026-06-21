from __future__ import annotations

from src.temporal_risk.connection import file_sha256, rollback_database
from src.temporal_risk.historical_ingestion.pipeline import (
    catalog_signature,
    deploy_phase2b_schema,
)
from src.temporal_risk.connection import connect_temporal
from test_phase2b_contracts import seed_phase2a_database


def test_phase2b_rollback_restores_exact_phase2a_hash_and_catalog(tmp_path) -> None:
    root = tmp_path / "temporal_platform"
    database = seed_phase2a_database(root)
    original_hash = file_sha256(database)
    result = deploy_phase2b_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    assert rollback_database(
        database,
        result["backup_path"],
        runtime_root=root,
    ) == "RESTORED_BACKUP"
    assert file_sha256(database) == original_hash
    connection = connect_temporal(database)
    try:
        catalog = catalog_signature(connection)
        assert (catalog["schema_count"], catalog["table_count"], catalog["view_count"]) == (
            5,
            17,
            0,
        )
    finally:
        connection.close()
