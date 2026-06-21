from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2b_contracts import shared_observed_ingestion


def test_ifrs9_readiness_ceiling_is_enforced() -> None:
    _, database, _ = shared_observed_ingestion()
    connection = connect_temporal(database)
    try:
        row = connection.execute(
            """
            SELECT data_status, activation_status
            FROM control.data_readiness_result
            WHERE capability_name = 'IFRS9_TEMPORAL_INPUTS'
            """
        ).fetchone()
        assert row[0] in {"NOT_READY", "NOT_ELIGIBLE"}
        assert row[0] != "READY_BUT_DISABLED"
        assert row[1] == "DISABLED_PENDING_FUTURE_PHASE"
    finally:
        connection.close()
