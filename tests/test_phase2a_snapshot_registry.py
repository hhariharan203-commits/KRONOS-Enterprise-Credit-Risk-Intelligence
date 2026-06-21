from __future__ import annotations

from pathlib import Path

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.pipeline import run_phase2a
from src.temporal_risk.snapshot_registry import inventory_identity_value


def test_snapshot_registers_metadata_only(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    database = root / "warehouse" / "temporal.duckdb"
    result = run_phase2a(
        database,
        runtime_root=root,
        evidence_dir=root / "evidence" / "phase2a",
        current_warehouse=CURRENT_WAREHOUSE,
        scored_portfolio=SCORED_PORTFOLIO,
        capture_protected_hashes=False,
    )
    assert result["status"] == "PHASE2A_SUCCESS"
    connection = connect_temporal(database)
    try:
        row = connection.execute(
            """
            SELECT history_mode, evidence_classification,
                   identity_continuity_status,
                   historical_analytics_eligible,
                   observation_date, reporting_date, origination_date
            FROM control.snapshot_registry
            """
        ).fetchone()
        assert row == (
            "PROCESS_TIME_ONLY",
            "SYNTHETIC_BASELINE",
            "NOT_ESTABLISHED",
            False,
            None,
            None,
            None,
        )
        assert connection.execute(
            "SELECT COUNT(*) FROM staging.stg_snapshot_manifest"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_inventory_identity_is_order_independent_and_dynamic() -> None:
    assert inventory_identity_value(["RUN-1"]) == "RUN-1"
    assert inventory_identity_value(["RUN-2", "RUN-1"]) == '["RUN-1","RUN-2"]'
    assert inventory_identity_value(["RUN-1", "RUN-2"]) == '["RUN-1","RUN-2"]'
    assert inventory_identity_value([]) is None
