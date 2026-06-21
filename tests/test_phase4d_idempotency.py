from __future__ import annotations

import shutil

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import PHASE4D_SUCCESS
from src.enterprise_data.risk_marts.runner import run_phase4d
from src.enterprise_data.risk_marts.source_catalog import (
    open_read_only,
    phase4d_view_row_counts,
    warehouse_inventory,
)


def test_phase4d_deployment_is_idempotent(tmp_path) -> None:
    database = tmp_path / "phase4d_idempotency.duckdb"
    shutil.copy2(WAREHOUSE_DB, database)

    first = run_phase4d(database)
    second = run_phase4d(database)
    assert first["status"] == PHASE4D_SUCCESS
    assert second["status"] == PHASE4D_SUCCESS

    connection = open_read_only(database)
    try:
        assert warehouse_inventory(connection) == {
            "schema_count": 5,
            "table_count": 58,
            "view_count": 10,
        }
        assert phase4d_view_row_counts(connection) == {
            "vw_concentration_risk_current": 27,
            "vw_portfolio_quality_current": 1,
            "vw_watchlist_intelligence_current": 16_378,
            "vw_model_governance_current": 3,
            "vw_enterprise_risk_summary_current": 1,
        }
    finally:
        connection.close()
