from __future__ import annotations

from pathlib import Path

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.pipeline import run_phase2a


def test_exact_quality_control_contract(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    result = run_phase2a(
        root / "warehouse" / "temporal.duckdb",
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2a",
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert result["quality"]["check_count"] == 27
    assert result["quality"]["failure_count"] == 0
    assert result["quality"]["warning_count"] == 3
    assert result["quality"]["status"] == "PASS_WITH_LIMITATIONS"
