from __future__ import annotations

from src.temporal_risk.connection import (
    WorkingDatabase,
    connect_temporal,
    discard_working_database,
    file_sha256,
    prepare_working_database,
    publish_working_database,
    rollback_database,
)
from src.temporal_risk.migration_readiness.source_catalog import (
    validate_exact_catalog,
)


def rollback_to_catalog(
    target_path,
    backup_path,
    *,
    runtime_root,
    expected_level: str,
    expected_sha256: str,
) -> dict:
    status = rollback_database(
        target_path,
        backup_path,
        runtime_root=runtime_root,
    )
    restored_hash = file_sha256(target_path)
    connection = connect_temporal(target_path, read_only=True)
    try:
        catalog = validate_exact_catalog(connection, expected_level)
    finally:
        connection.close()
    return {
        "status": status,
        "restored_sha256": restored_hash,
        "hash_matches": restored_hash == expected_sha256,
        "catalog": catalog,
    }


__all__ = [
    "WorkingDatabase",
    "prepare_working_database",
    "publish_working_database",
    "discard_working_database",
    "rollback_to_catalog",
]
