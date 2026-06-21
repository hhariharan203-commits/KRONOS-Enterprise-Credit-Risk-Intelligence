from __future__ import annotations

from pathlib import Path

from src.temporal_risk.connection import file_sha256
from src.temporal_risk.historical_ingestion.config import (
    OBSERVED_INBOUND_DIR,
    ROOT_DIR,
    SIMULATED_INBOUND_DIR,
    TEMPORAL_ROOT,
)
from src.temporal_risk.historical_ingestion.contracts import (
    HistoricalContractError,
    OBSERVED_TEMPORAL,
    SIMULATED_TEMPORAL,
)


def repository_relative(
    path: Path,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT_DIR.resolve()).as_posix()
    except ValueError:
        runtime = Path(runtime_root).resolve()
        return (
            Path("temporal_platform")
            / resolved.relative_to(runtime)
        ).as_posix()


def _contains_symlink(path: Path, root: Path) -> bool:
    current = path
    while current != root and current != current.parent:
        if current.is_symlink():
            return True
        current = current.parent
    return root.is_symlink()


def allowed_inbound_root(
    history_mode: str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> Path:
    runtime = Path(runtime_root).resolve()
    if history_mode == OBSERVED_TEMPORAL:
        return (
            OBSERVED_INBOUND_DIR.resolve()
            if runtime == TEMPORAL_ROOT.resolve()
            else runtime / "inbound" / "observed"
        )
    if history_mode == SIMULATED_TEMPORAL:
        return (
            SIMULATED_INBOUND_DIR.resolve()
            if runtime == TEMPORAL_ROOT.resolve()
            else runtime / "inbound" / "simulated"
        )
    raise HistoricalContractError(f"Unsupported history mode: {history_mode}")


def validate_inbound_file(
    path: Path | str,
    history_mode: str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> Path:
    source = Path(path).expanduser()
    if source.is_absolute():
        resolved = source.resolve()
    else:
        root_candidate = Path(runtime_root).resolve()
        resolved = (
            (ROOT_DIR / source).resolve()
            if root_candidate == TEMPORAL_ROOT.resolve()
            else (root_candidate / source).resolve()
        )
    root = allowed_inbound_root(history_mode, runtime_root=runtime_root)
    if not resolved.is_relative_to(root):
        raise HistoricalContractError("Historical source path is not allowlisted.")
    if _contains_symlink(resolved, root):
        raise HistoricalContractError("Symbolic-link traversal is prohibited.")
    if not resolved.is_file():
        raise HistoricalContractError(f"Historical source is unavailable: {resolved}")
    if resolved.name.startswith(".") or resolved.suffix.lower() in {
        ".duckdb",
        ".wal",
        ".tmp",
    }:
        raise HistoricalContractError("Working database assets are not valid sources.")
    return resolved


def source_profile(
    path: Path,
    source_format: str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> dict:
    normalized_format = source_format.strip().upper()
    if normalized_format not in {"CSV", "PARQUET"}:
        raise HistoricalContractError(f"Unsupported source format: {source_format}")
    return {
        "path": path,
        "relative_path": repository_relative(path, runtime_root=runtime_root),
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
        "source_format": normalized_format,
    }
