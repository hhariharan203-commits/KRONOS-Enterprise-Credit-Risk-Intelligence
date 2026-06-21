from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.migration_readiness.pipeline import (
    evaluate_migration_readiness,
    evaluate_migration_readiness_safe,
)
from test_phase2c_contracts import two_snapshot_environment


def test_exact_readiness_evaluation_is_idempotent() -> None:
    root, database, snapshot_ids = two_snapshot_environment()
    first = evaluate_migration_readiness(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    repeated = evaluate_migration_readiness(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    assert first["status"] == "PHASE2C_READINESS_PUBLISHED"
    assert repeated["status"] == "SKIPPED_ALREADY_PUBLISHED"


def test_same_contract_version_with_changed_hash_is_a_conflict() -> None:
    root, database, snapshot_ids = two_snapshot_environment()
    evaluate_migration_readiness(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    connection = connect_temporal(
        database,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    try:
        connection.execute(
            """
            UPDATE control.migration_transition_contract
            SET contract_hash = ?
            WHERE contract_name = 'RISK_GRADE_DOMAIN_V1'
              AND contract_version = '1'
            """,
            ["A" * 64],
        )
    finally:
        connection.close()
    result = evaluate_migration_readiness_safe(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2C_PAIR_CONFLICT"


def test_changed_source_evidence_is_a_conflict() -> None:
    root, database, snapshot_ids = two_snapshot_environment()
    evaluate_migration_readiness(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    connection = connect_temporal(
        database,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    try:
        connection.execute(
            """
            UPDATE core.dim_historical_snapshot
            SET source_sha256 = ?
            WHERE snapshot_id = ?
            """,
            ["B" * 64, snapshot_ids[0]],
        )
    finally:
        connection.close()
    result = evaluate_migration_readiness_safe(
        state_field="risk_grade",
        earlier_snapshot_id=snapshot_ids[0],
        later_snapshot_id=snapshot_ids[1],
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2c",
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2C_PAIR_CONFLICT"
