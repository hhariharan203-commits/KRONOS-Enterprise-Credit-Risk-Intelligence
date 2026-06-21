from __future__ import annotations

from src.temporal_risk.historical_ingestion.pipeline import run_historical_ingestion
from test_phase2b_contracts import deployed_phase2b, write_manifest


def test_simulated_source_remains_ineligible_for_ifrs9_and_true_oot() -> None:
    root, database = deployed_phase2b()
    manifest = write_manifest(root, mode="simulated")
    result = run_historical_ingestion(
        manifest,
        database_path=database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2b",
        capture_protected_hashes=False,
    )
    statuses = {
        row["capability_name"]: row["data_status"] for row in result["readiness"]
    }
    assert statuses["TRUE_OOT_INPUTS"] == "NOT_ELIGIBLE"
    assert statuses["IFRS9_TEMPORAL_INPUTS"] == "NOT_ELIGIBLE"
