from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2c_contracts import shared_published_readiness


def test_exactly_ten_reconciliations_pass() -> None:
    _, database, _, result = shared_published_readiness()
    connection = connect_temporal(database)
    try:
        rows = connection.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END)
            FROM control.migration_reconciliation_result
            WHERE readiness_run_id = ?
            """,
            [result["readiness_run_id"]],
        ).fetchone()
        assert tuple(rows) == (10, 10)
    finally:
        connection.close()
