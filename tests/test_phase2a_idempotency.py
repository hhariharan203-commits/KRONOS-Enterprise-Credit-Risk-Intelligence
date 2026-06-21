from __future__ import annotations

from pathlib import Path

from src.temporal_risk.config import CURRENT_WAREHOUSE, SCORED_PORTFOLIO
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.pipeline import run_phase2a


def test_repeat_deployment_preserves_business_idempotency(tmp_path: Path) -> None:
    root = tmp_path / "temporal_platform"
    database = root / "warehouse" / "temporal.duckdb"
    kwargs = {
        "runtime_root": root,
        "evidence_dir": root / "evidence" / "phase2a",
        "current_warehouse": CURRENT_WAREHOUSE,
        "scored_portfolio": SCORED_PORTFOLIO,
        "capture_protected_hashes": False,
    }
    run_phase2a(database, **kwargs)
    run_phase2a(database, **kwargs)
    connection = connect_temporal(database)
    try:
        business_counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM control.source_asset),
                (SELECT COUNT(*) FROM control.source_column),
                (SELECT COUNT(*) FROM control.temporal_contract),
                (SELECT COUNT(*) FROM control.snapshot_registry),
                (SELECT COUNT(*) FROM staging.stg_snapshot_manifest),
                (SELECT COUNT(*) FROM control.lineage_node),
                (SELECT COUNT(*) FROM control.lineage_edge),
                (SELECT COUNT(*) FROM control.column_lineage)
            """
        ).fetchone()
        assert business_counts == (1, 63, 2, 1, 1, 5, 4, 4)
        operational = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM control.deployment_run),
                (SELECT COUNT(*) FROM control.temporal_quality_result),
                (SELECT COUNT(*) FROM control.reconciliation_result),
                (SELECT COUNT(*) FROM control.publish_status)
            """
        ).fetchone()
        assert operational == (2, 54, 18, 6)
    finally:
        connection.close()
