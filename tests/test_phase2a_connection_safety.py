from __future__ import annotations

from pathlib import Path

import pytest

from src.temporal_risk.config import CURRENT_WAREHOUSE
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.contracts import Phase2AValidationError
from src.temporal_risk.pipeline import run_phase2a_safe


def test_connections_default_to_read_only(tmp_path: Path) -> None:
    missing = tmp_path / "missing.duckdb"
    with pytest.raises(FileNotFoundError):
        connect_temporal(missing)
    assert not missing.exists()


def test_current_warehouse_can_never_be_a_write_target() -> None:
    with pytest.raises(Phase2AValidationError):
        connect_temporal(
            CURRENT_WAREHOUSE,
            read_only=False,
            deployment_authorized=True,
        )


def test_writable_target_requires_explicit_authorization(tmp_path: Path) -> None:
    target = tmp_path / "temporal_platform" / "warehouse" / "test.duckdb"
    with pytest.raises(Phase2AValidationError):
        connect_temporal(target, read_only=False, runtime_root=tmp_path)


def test_invalid_target_writes_no_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "temporal_platform" / "evidence" / "phase2a"
    result = run_phase2a_safe(
        database_path=CURRENT_WAREHOUSE,
        runtime_root=tmp_path / "temporal_platform",
        evidence_dir=evidence,
    )
    assert result["status"] == "TEMPORAL_PLATFORM_UNAVAILABLE"
    assert not evidence.exists()


def test_missing_specification_writes_no_evidence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import src.temporal_risk.pipeline as pipeline

    root = tmp_path / "temporal_platform"
    evidence = root / "evidence" / "phase2a"
    monkeypatch.setattr(
        pipeline,
        "SPECIFICATION_NAMES",
        ("MISSING_CONTROLLED_SPECIFICATION.md",),
    )
    result = pipeline.run_phase2a_safe(
        database_path=root / "warehouse" / "test.duckdb",
        runtime_root=root,
        evidence_dir=evidence,
    )
    assert result["status"] == "BASELINE_SPECIFICATION_MISSING"
    assert not evidence.exists()
