from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.pipeline import run_phase2a


def test_exact_reconciliation_contract(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    result = run_phase2a(
        root / "warehouse" / "temporal.duckdb",
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2a",
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert result["reconciliation"]["reconciliation_count"] == 9
    assert result["reconciliation"]["failure_count"] == 0
    assert result["reconciliation"]["status"] == "PASS"


def test_multiple_run_and_model_inventories_are_governed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import src.temporal_risk.pipeline as pipeline
    import src.temporal_risk.source_registry as source_registry

    source_root = tmp_path / "source"
    source_root.mkdir()
    source = source_root / "multi_inventory.csv"
    pd.DataFrame(
        {
            "borrower_id": ["B1", "B2", "B3", "B4"],
            "run_id": ["RUN-2", "RUN-1", "RUN-2", "RUN-1"],
            "model_version": ["M2", "M1", "M2", "M1"],
            "timestamp": ["2026-01-01T00:00:00+00:00"] * 4,
            "scoring_status": ["SCORED"] * 4,
        }
    ).to_csv(source, index=False)
    monkeypatch.setattr(source_registry, "ROOT_DIR", source_root)
    monkeypatch.setattr(pipeline, "SCORED_PORTFOLIO", source)
    monkeypatch.setattr(pipeline, "validate_source_path", lambda _path: True)

    root = tmp_path / "temporal_platform"
    database = root / "warehouse" / "temporal.duckdb"
    result = run_phase2a(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2a",
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=source,
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2A_SUCCESS"
    assert result["reconciliation"]["failure_count"] == 0
    connection = connect_temporal(database)
    try:
        row = connection.execute(
            """
            SELECT source_run_id, source_model_version
            FROM control.snapshot_registry
            """
        ).fetchone()
        assert row == (None, None)
    finally:
        connection.close()
