from __future__ import annotations

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.pipeline import run_phase2a_safe
from test_phase2b_contracts import deployed_phase2b


def test_phase2a_upgrade_guard_runs_before_evidence_write() -> None:
    root, database = deployed_phase2b()
    evidence = root / "evidence" / "phase2a_guard"
    result = run_phase2a_safe(
        database,
        runtime_root=root,
        evidence_dir=evidence,
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2A_UPGRADE_PRESENT"
    assert not evidence.exists()
