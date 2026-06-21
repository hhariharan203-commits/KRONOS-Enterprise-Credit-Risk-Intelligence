from __future__ import annotations

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.historical_ingestion.pipeline import (
    deploy_phase2b_schema,
)
from src.temporal_risk.pipeline import run_phase2a_safe
from test_phase2c_contracts import deployed_phase2c


def test_earlier_phase_guards_recognize_exact_phase2c_catalog() -> None:
    root, database = deployed_phase2c()
    phase2a_evidence = root / "evidence" / "phase2a_after_phase2c"
    phase2a = run_phase2a_safe(
        database,
        runtime_root=root,
        evidence_dir=phase2a_evidence,
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert phase2a["status"] == "PHASE2A_UPGRADE_PRESENT"
    assert not phase2a_evidence.exists()

    phase2b_evidence = root / "evidence" / "phase2b_after_phase2c"
    phase2b = deploy_phase2b_schema(
        database,
        runtime_root=root,
        evidence_dir=phase2b_evidence,
        capture_protected_hashes=False,
    )
    assert phase2b["status"] == "PHASE2B_UPGRADE_PRESENT"
    assert not phase2b_evidence.exists()
