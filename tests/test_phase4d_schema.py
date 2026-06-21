from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import (
    EXPECTED_EXISTING_MART_ROWS,
    MINIMUM_HISTORY_MART_ROWS,
)
from src.enterprise_data.risk_marts.source_catalog import (
    VIEW_NAMES,
    existing_mart_row_counts,
    open_read_only,
    warehouse_inventory,
)


def test_phase4d_adds_only_expected_views() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        views = {
            str(row[0])
            for row in connection.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'mart' AND table_type = 'VIEW'
                """
            ).fetchall()
        }
        inventory = warehouse_inventory(connection)
        assert set(VIEW_NAMES).issubset(views)
        assert inventory["schema_count"] == 5
        assert inventory["table_count"] == 58
        assert inventory["view_count"] == 10
        mart_rows = existing_mart_row_counts(connection)
        for mart, expected in EXPECTED_EXISTING_MART_ROWS.items():
            assert mart_rows[mart] == expected
        for mart, minimum in MINIMUM_HISTORY_MART_ROWS.items():
            assert mart_rows[mart] >= minimum
    finally:
        connection.close()
