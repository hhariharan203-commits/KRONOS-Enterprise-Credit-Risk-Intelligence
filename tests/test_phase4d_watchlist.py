from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import EXPECTED_WATCHLIST_COUNT
from src.enterprise_data.risk_marts.source_catalog import open_read_only


def test_watchlist_is_current_state_and_deterministically_ranked() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        count, distinct_ranks, min_rank, max_rank, invalid_flags = (
            connection.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT priority_rank),
                    MIN(priority_rank),
                    MAX(priority_rank),
                    SUM(CASE WHEN watchlist_flag <> 1 THEN 1 ELSE 0 END)
                FROM mart.vw_watchlist_intelligence_current
                """
            ).fetchone()
        )
        assert count == EXPECTED_WATCHLIST_COUNT
        assert distinct_ranks == EXPECTED_WATCHLIST_COUNT
        assert min_rank == 1
        assert max_rank == EXPECTED_WATCHLIST_COUNT
        assert invalid_flags == 0

        expected_first = connection.execute(
            """
            SELECT borrower_key
            FROM mart.mart_credit_risk_current
            WHERE watchlist_flag = 1
            ORDER BY early_warning_score DESC, pd_score DESC,
                     ead DESC, borrower_key ASC
            LIMIT 1
            """
        ).fetchone()[0]
        actual_first = connection.execute(
            """
            SELECT borrower_key
            FROM mart.vw_watchlist_intelligence_current
            WHERE priority_rank = 1
            """
        ).fetchone()[0]
        assert actual_first == expected_first
    finally:
        connection.close()
