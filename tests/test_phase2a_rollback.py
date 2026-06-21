from __future__ import annotations

from pathlib import Path

from src.temporal_risk.connection import (
    connect_temporal,
    file_sha256,
    prepare_working_database,
    publish_working_database,
    rollback_database,
)


def test_file_based_rollback_restores_prior_database(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    target = root / "warehouse" / "temporal.duckdb"
    connection = connect_temporal(
        target,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    connection.execute("CREATE TABLE baseline(value INTEGER)")
    connection.execute("INSERT INTO baseline VALUES (1)")
    connection.close()
    original_hash = file_sha256(target)

    working = prepare_working_database(target, runtime_root=root)
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    connection.execute("INSERT INTO baseline VALUES (2)")
    connection.close()
    publish_working_database(working)
    assert file_sha256(target) != original_hash

    assert rollback_database(
        target,
        working.backup_path,
        runtime_root=root,
    ) == "RESTORED_BACKUP"
    assert file_sha256(target) == original_hash


def test_first_deployment_rollback_removes_only_temporal_target(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    target = root / "warehouse" / "temporal.duckdb"
    connection = connect_temporal(
        target,
        read_only=False,
        deployment_authorized=True,
        runtime_root=root,
    )
    connection.close()
    assert rollback_database(target, None, runtime_root=root) == "REMOVED_FIRST_DEPLOYMENT"
    assert not target.exists()
