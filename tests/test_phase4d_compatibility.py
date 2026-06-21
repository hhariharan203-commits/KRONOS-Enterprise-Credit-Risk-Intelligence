from __future__ import annotations

import shutil
from pathlib import Path

from src.enterprise_data.config import ROOT_DIR, WAREHOUSE_DB
from src.enterprise_data.risk_marts.contracts import (
    MARTS_UNAVAILABLE,
    PHASE4D_SUCCESS,
)
from src.enterprise_data.risk_marts.runner import run_phase4d
from src.enterprise_data.risk_marts.source_catalog import open_read_only


CONTROL_TABLES = (
    "etl_batch",
    "etl_job_run",
    "data_quality_result",
    "etl_quality_summary",
    "reconciliation_result",
    "publish_status",
    "lineage_node",
    "lineage_edge",
    "column_lineage",
)


def _control_counts(database: Path) -> dict[str, int]:
    connection = open_read_only(database)
    try:
        return {
            table: int(
                connection.execute(
                    f"SELECT COUNT(*) FROM control.{table}"
                ).fetchone()[0]
            )
            for table in CONTROL_TABLES
        }
    finally:
        connection.close()


def test_control_tables_and_existing_marts_remain_unchanged(
    tmp_path,
) -> None:
    database = tmp_path / "phase4d_compatibility.duckdb"
    shutil.copy2(WAREHOUSE_DB, database)
    before = _control_counts(database)

    result = run_phase4d(database)

    assert result["status"] == PHASE4D_SUCCESS
    assert _control_counts(database) == before


def test_phase4d_is_not_an_application_dependency() -> None:
    app_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT_DIR / "app").glob("*.py")
    )
    assert "risk_marts" not in app_sources


def test_safe_entry_point_never_propagates_failure(tmp_path) -> None:
    missing_database = tmp_path / "missing.duckdb"
    result = run_phase4d(missing_database)
    assert result["status"] == MARTS_UNAVAILABLE
    assert result["application_impact"].startswith("NONE")
    assert not missing_database.exists()


def test_rollback_sql_owns_only_phase4d_views() -> None:
    rollback = (
        ROOT_DIR / "sql" / "phase4d" / "rollback_phase4d_views.sql"
    ).read_text(encoding="utf-8")
    assert rollback.count("DROP VIEW IF EXISTS") == 5
    assert "DROP TABLE" not in rollback.upper()
    assert "mart_credit_risk_current" not in rollback
