from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2c_contracts import shared_published_readiness


def test_four_readiness_results_remain_disabled() -> None:
    _, database, _, result = shared_published_readiness()
    connection = connect_temporal(database)
    try:
        rows = connection.execute(
            """
            SELECT capability_name, data_status, activation_status,
                   governance_score
            FROM control.migration_readiness_result
            WHERE readiness_run_id = ?
            ORDER BY capability_name
            """,
            [result["readiness_run_id"]],
        ).fetchall()
        assert len(rows) == 4
        assert all(row[1] == "READY_BUT_DISABLED" for row in rows)
        assert all(row[2] == "DISABLED_PENDING_FUTURE_PHASE" for row in rows)
        assert all(str(row[3]) == "100.00" for row in rows)
    finally:
        connection.close()
