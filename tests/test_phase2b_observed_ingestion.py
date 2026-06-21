from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2b_contracts import shared_observed_ingestion


def test_observed_snapshot_is_stored_without_analytics() -> None:
    _, database, result = shared_observed_ingestion()
    assert result["status"] == "PHASE2B_INGESTION_SUCCESS"
    assert result["quality"]["check_count"] == 36
    assert result["reconciliation"]["reconciliation_count"] == 12
    connection = connect_temporal(database)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM core.fact_historical_credit_observation"
        ).fetchone()[0] == 3
        assert connection.execute(
            "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'mart'"
        ).fetchone()[0] == 0
    finally:
        connection.close()
