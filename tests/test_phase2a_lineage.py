from __future__ import annotations

from pathlib import Path

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.pipeline import run_phase2a


def test_exact_lineage_contract(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    result = run_phase2a(
        root / "warehouse" / "temporal.duckdb",
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2a",
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert result["lineage"] == {
        "node_count": 5,
        "edge_count": 4,
        "column_lineage_count": 4,
        "complete": True,
    }
