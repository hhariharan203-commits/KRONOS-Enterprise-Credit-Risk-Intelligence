from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse


def test_phase4a_schemas_and_tables_exist() -> None:
    connection = connect_warehouse(WAREHOUSE_DB, read_only=True)
    try:
        schemas = {
            row[0]
            for row in connection.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                """
            ).fetchall()
        }
        assert {"control", "staging", "reference", "core", "mart"}.issubset(schemas)

        tables = {
            f"{schema}.{table}"
            for schema, table in connection.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                """
            ).fetchall()
        }
        assert {
            "control.etl_batch",
            "control.source_asset",
            "control.artifact_registry",
            "staging.stg_scored_portfolio",
            "core.fact_credit_risk_snapshot",
            "core.dim_borrower",
            "core.dim_credit_facility",
            "mart.mart_credit_risk_current",
            "mart.mart_ifrs9_stage_current",
            "mart.mart_ews_current",
            "mart.mart_model_risk",
            "mart.mart_executive_current",
        }.issubset(tables)

        source_columns = {
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'source_asset'
                """
            ).fetchall()
        }
        artifact_columns = {
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'artifact_registry'
                """
            ).fetchall()
        }
        assert "is_current" in source_columns
        assert "is_current" in artifact_columns
    finally:
        connection.close()
