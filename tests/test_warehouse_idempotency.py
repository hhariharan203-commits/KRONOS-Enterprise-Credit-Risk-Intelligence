from __future__ import annotations

import shutil

from src.enterprise_data.config import CSV_SOURCES, WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse
from src.enterprise_data.pipeline import run_phase4a_pipeline


def test_repeat_load_does_not_duplicate_business_facts(tmp_path) -> None:
    copied_database = tmp_path / "kronos_idempotency.duckdb"
    shutil.copy2(WAREHOUSE_DB, copied_database)

    before = connect_warehouse(copied_database, read_only=True)
    try:
        before_count = before.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0]
        before_market = before.execute(
            "SELECT COUNT(*) FROM core.fact_market_observation"
        ).fetchone()[0]
    finally:
        before.close()

    result = run_phase4a_pipeline(copied_database)
    assert result["status"] == "SUCCESS"
    assert result["loaded_source_count"] == 0
    assert result["skipped_source_count"] == len(CSV_SOURCES)
    assert result["credit_core"]["snapshot_rows_inserted"] == 0

    after = connect_warehouse(copied_database, read_only=True)
    try:
        assert after.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0] == before_count
        assert after.execute(
            "SELECT COUNT(*) FROM core.fact_market_observation"
        ).fetchone()[0] == before_market
    finally:
        after.close()
