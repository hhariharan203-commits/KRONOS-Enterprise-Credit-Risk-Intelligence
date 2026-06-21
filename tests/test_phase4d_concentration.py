from __future__ import annotations

import math

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import (
    EXPECTED_DIMENSION_COUNTS,
    EXPECTED_TOTAL_EAD,
)
from src.enterprise_data.risk_marts.source_catalog import open_read_only


def test_concentration_categories_and_exposure_reconcile() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        rows = connection.execute(
            """
            SELECT
                dimension_type,
                COUNT(*),
                SUM(total_ead),
                SUM(exposure_share),
                MIN(hhi),
                MAX(hhi),
                SUM(hhi_contribution)
            FROM mart.vw_concentration_risk_current
            GROUP BY dimension_type
            """
        ).fetchall()
        assert len(rows) == 4
        for dimension, count, ead, share, min_hhi, max_hhi, hhi_sum in rows:
            assert count == EXPECTED_DIMENSION_COUNTS[dimension]
            assert math.isclose(ead, EXPECTED_TOTAL_EAD, abs_tol=0.01)
            assert math.isclose(share, 1.0, abs_tol=1e-10)
            assert math.isclose(min_hhi, max_hhi, abs_tol=1e-15)
            assert math.isclose(min_hhi, hhi_sum, abs_tol=1e-15)
    finally:
        connection.close()
