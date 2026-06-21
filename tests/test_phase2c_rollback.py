from __future__ import annotations

from src.temporal_risk.connection import file_sha256
from src.temporal_risk.migration_readiness.pipeline import (
    deploy_phase2c_schema,
    evaluate_migration_readiness,
)
from src.temporal_risk.migration_readiness.publisher import rollback_to_catalog
from test_phase2b_contracts import deployed_phase2b
from test_phase2c_contracts import two_snapshot_environment


def test_schema_rollback_restores_exact_phase2b_database() -> None:
    root, database = deployed_phase2b()
    original_hash = file_sha256(database)
    result = deploy_phase2c_schema(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    rollback = rollback_to_catalog(
        database,
        result["backup_path"],
        runtime_root=root,
        expected_level="PHASE2B",
        expected_sha256=original_hash,
    )
    assert rollback["hash_matches"]
    assert rollback["catalog"]["table_count"] == 36


def test_readiness_rollback_restores_exact_phase2c_database() -> None:
    root, database, snapshot_ids = two_snapshot_environment()
    original_hash = file_sha256(database)
    result = evaluate_migration_readiness(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    rollback = rollback_to_catalog(
        database,
        result["backup_path"],
        runtime_root=root,
        expected_level="PHASE2C",
        expected_sha256=original_hash,
    )
    assert rollback["hash_matches"]
    assert rollback["catalog"]["table_count"] == 46
