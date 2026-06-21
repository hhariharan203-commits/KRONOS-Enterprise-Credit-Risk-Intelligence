from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.temporal_risk.config import (
    CURRENT_WAREHOUSE,
    TEMPORAL_BACKUP_DIR,
    TEMPORAL_DATABASE,
    TEMPORAL_ROOT,
)
from src.temporal_risk.contracts import Phase2AValidationError


@dataclass(frozen=True)
class WorkingDatabase:
    target_path: Path
    working_path: Path
    backup_path: Path | None = None


def _duckdb():
    try:
        import duckdb
    except ImportError as exc:
        raise Phase2AValidationError("DuckDB is required for Phase 2A.") from exc
    return duckdb


def _resolved(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def assert_temporal_target(
    database_path: Path | str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> Path:
    path = _resolved(database_path)
    root = _resolved(runtime_root)
    current = _resolved(CURRENT_WAREHOUSE)
    current_dir = current.parent
    if path == current or path.is_relative_to(current_dir):
        raise Phase2AValidationError("Current KRONOS warehouse path is protected.")
    if not path.is_relative_to(root):
        raise Phase2AValidationError("Writable Phase 2A path is outside temporal_platform.")
    return path


def assert_evidence_target(
    evidence_path: Path | str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> Path:
    path = _resolved(evidence_path)
    root = _resolved(runtime_root)
    expected_root = root / "evidence"
    if not path.is_relative_to(expected_root):
        raise Phase2AValidationError(
            "Phase 2A evidence path is outside temporal_platform/evidence."
        )
    return path


def connect_temporal(
    database_path: Path | str = TEMPORAL_DATABASE,
    *,
    read_only: bool = True,
    deployment_authorized: bool = False,
    runtime_root: Path | str = TEMPORAL_ROOT,
):
    path = _resolved(database_path)
    if read_only:
        if not path.is_file():
            raise FileNotFoundError(f"Temporal database not found: {path}")
        return _duckdb().connect(str(path), read_only=True)
    if not deployment_authorized:
        raise Phase2AValidationError("Writable connection requires deployment authorization.")
    path = assert_temporal_target(path, runtime_root=runtime_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    return _duckdb().connect(str(path), read_only=False)


def prepare_working_database(
    target_path: Path | str = TEMPORAL_DATABASE,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> WorkingDatabase:
    target = assert_temporal_target(target_path, runtime_root=runtime_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    working_dir = Path(tempfile.gettempdir()) / "kronos_phase2a"
    working_dir.mkdir(parents=True, exist_ok=True)
    working = working_dir / f"phase2a-{uuid4().hex}.working.duckdb"
    backup = None
    if target.is_file():
        digest = file_sha256(target)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = (
            _resolved(runtime_root) / "backups"
            if _resolved(runtime_root) != _resolved(TEMPORAL_ROOT)
            else TEMPORAL_BACKUP_DIR
        )
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"kronos_temporal_risk_{stamp}_{digest[:16]}.duckdb"
        shutil.copy2(target, backup)
        if file_sha256(backup) != digest:
            raise Phase2AValidationError("Temporal database backup verification failed.")
        shutil.copy2(target, working)
    return WorkingDatabase(target_path=target, working_path=working, backup_path=backup)


def publish_working_database(database: WorkingDatabase) -> None:
    if not database.working_path.is_file():
        raise Phase2AValidationError("Validated working database is unavailable.")
    database.target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.replace(database.working_path, database.target_path)
    except PermissionError:
        shutil.copyfile(database.working_path, database.target_path)
        if file_sha256(database.working_path) != file_sha256(database.target_path):
            raise Phase2AValidationError("Published database copy verification failed.")
        database.working_path.unlink(missing_ok=True)


def discard_working_database(database: WorkingDatabase) -> None:
    for path in (
        database.working_path,
        Path(f"{database.working_path}.wal"),
    ):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def rollback_database(
    target_path: Path | str,
    backup_path: Path | str | None,
    *,
    runtime_root: Path | str,
) -> str:
    target = assert_temporal_target(target_path, runtime_root=runtime_root)
    if backup_path is None:
        target.unlink(missing_ok=True)
        Path(f"{target}.wal").unlink(missing_ok=True)
        return "REMOVED_FIRST_DEPLOYMENT"
    backup = assert_temporal_target(backup_path, runtime_root=runtime_root)
    if not backup.is_file():
        raise Phase2AValidationError("Rollback backup is unavailable.")
    replacement = target.parent / f".rollback-{uuid4().hex}.duckdb"
    shutil.copy2(backup, replacement)
    if file_sha256(replacement) != file_sha256(backup):
        replacement.unlink(missing_ok=True)
        raise Phase2AValidationError("Rollback copy verification failed.")
    try:
        os.replace(replacement, target)
    except PermissionError:
        shutil.copyfile(replacement, target)
        if file_sha256(replacement) != file_sha256(target):
            replacement.unlink(missing_ok=True)
            raise Phase2AValidationError("Rollback publication verification failed.")
        replacement.unlink(missing_ok=True)
    return "RESTORED_BACKUP"


def file_sha256(path: Path | str) -> str:
    import hashlib

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()
