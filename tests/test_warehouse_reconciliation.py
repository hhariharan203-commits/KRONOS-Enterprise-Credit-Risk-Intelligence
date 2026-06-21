from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse


def test_latest_successful_batch_reconciles_to_source() -> None:
    connection = connect_warehouse(WAREHOUSE_DB, read_only=True)
    try:
        batch_id = connection.execute(
            """
            SELECT etl_batch_id
            FROM control.etl_batch
            WHERE status = 'SUCCESS'
            ORDER BY completed_at DESC
            LIMIT 1
            """
        ).fetchone()[0]
        total, failures = connection.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN status <> 'PASS' THEN 1 ELSE 0 END)
            FROM control.reconciliation_result
            WHERE etl_batch_id = ?
            """,
            [batch_id],
        ).fetchone()
        assert total >= 14
        assert failures == 0

        executive = connection.execute(
            """
            SELECT portfolio_count, total_ead, average_pd, average_lgd
            FROM mart.mart_executive_current
            """
        ).fetchone()
        assert executive[0] == 50_000
        assert round(executive[1], 2) == 837_946_260.46
        assert round(executive[2], 6) == 0.234783
        assert round(executive[3], 6) == 0.547166
    finally:
        connection.close()
