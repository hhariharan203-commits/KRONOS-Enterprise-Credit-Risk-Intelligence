from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from src.enterprise_data.config import WAREHOUSE_DB


class WarehouseDependencyError(RuntimeError):
    """Raised when the optional warehouse dependency is unavailable."""


@dataclass(frozen=True)
class WorkingDatabase:
    target_path: Path
    working_path: Path


def _duckdb():
    try:
        import duckdb
    except ImportError as exc:
        raise WarehouseDependencyError(
            "DuckDB is required only for the optional Phase 4A warehouse. "
            "Existing KRONOS CSV workflows remain available."
        ) from exc
    return duckdb


def connect_warehouse(
    database_path: Path | str = WAREHOUSE_DB,
    *,
    read_only: bool = False,
):
    path = Path(database_path)
    if not read_only:
        path.parent.mkdir(parents=True, exist_ok=True)
    return _duckdb().connect(str(path), read_only=read_only)


def prepare_working_database(
    target_path: Path | str = WAREHOUSE_DB,
) -> WorkingDatabase:
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    working_dir = Path(tempfile.gettempdir()) / "kronos_phase4a"
    working_dir.mkdir(parents=True, exist_ok=True)
    working = working_dir / f"kronos_risk_{uuid4().hex}.duckdb"
    if target.is_file():
        shutil.copy2(target, working)
    return WorkingDatabase(target_path=target, working_path=working)


def publish_working_database(database: WorkingDatabase) -> None:
    database.target_path.parent.mkdir(parents=True, exist_ok=True)
    # The workspace can deny child-file deletion while still permitting writes.
    # Copying the closed database avoids DuckDB WAL operations in OneDrive.
    shutil.copyfile(database.working_path, database.target_path)
    target_wal = Path(f"{database.target_path}.wal")
    if target_wal.exists():
        target_wal.write_bytes(b"")


def discard_working_database(database: WorkingDatabase) -> None:
    for path in (
        database.working_path,
        Path(f"{database.working_path}.wal"),
    ):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def warehouse_available(database_path: Path | str = WAREHOUSE_DB) -> bool:
    try:
        _duckdb()
    except WarehouseDependencyError:
        return False
    return Path(database_path).is_file()
