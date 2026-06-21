from __future__ import annotations

import math

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import (
    EXPECTED_PORTFOLIO_COUNT,
    EXPECTED_TOTAL_EAD,
    EXPECTED_WATCHLIST_COUNT,
)
from src.enterprise_data.risk_marts.source_catalog import open_read_only


def test_portfolio_quality_metrics_reconcile() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        row = connection.execute(
            """
            SELECT
                portfolio_count,
                total_ead,
                watchlist_count,
                stage_1_count + stage_2_count + stage_3_count,
                stage_1_exposure + stage_2_exposure + stage_3_exposure,
                current_credit_loss_proxy,
                temporal_quality
            FROM mart.vw_portfolio_quality_current
            """
        ).fetchone()
        assert row[0] == EXPECTED_PORTFOLIO_COUNT
        assert math.isclose(row[1], EXPECTED_TOTAL_EAD, abs_tol=0.01)
        assert row[2] == EXPECTED_WATCHLIST_COUNT
        assert row[3] == EXPECTED_PORTFOLIO_COUNT
        assert math.isclose(row[4], EXPECTED_TOTAL_EAD, abs_tol=0.01)
        assert row[5] > 0
        assert row[6] == "PROCESS TIME ONLY"
    finally:
        connection.close()
