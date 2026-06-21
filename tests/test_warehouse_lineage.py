from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse


def test_latest_batch_has_complete_mart_lineage() -> None:
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
        mart_columns = connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = 'mart' AND table_name LIKE 'mart_%'
            """
        ).fetchone()[0]
        lineage_columns = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.column_lineage
            WHERE etl_batch_id = ? AND target_schema = 'mart'
            """,
            [batch_id],
        ).fetchone()[0]
        assert lineage_columns >= mart_columns

        source_edges = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.lineage_edge
            WHERE etl_batch_id = ?
              AND transformation_name = 'READ_ONLY_MIRROR'
            """,
            [batch_id],
        ).fetchone()[0]
        assert source_edges == 18
    finally:
        connection.close()
