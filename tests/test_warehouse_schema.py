from __future__ import annotations

import duckdb

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse
from src.enterprise_data.schema_manager import (
    ensure_reconciliation_result_schema,
    refresh_control_views,
)


RECONCILIATION_COLUMNS = [
    "reconciliation_id",
    "etl_batch_id",
    "source_asset_id",
    "reconciliation_name",
    "source_value",
    "warehouse_value",
    "absolute_difference",
    "tolerance",
    "status",
    "reconciled_at",
    "job_id",
    "source_count",
    "staging_count",
    "core_count",
    "mart_count",
    "variance",
]

DATA_QUALITY_COLUMNS = [
    "quality_result_id",
    "etl_batch_id",
    "source_asset_id",
    "check_name",
    "check_scope",
    "status",
    "actual_value",
    "expected_value",
    "details",
    "checked_at",
]


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

        reconciliation_columns = [
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'reconciliation_result'
                ORDER BY ordinal_position
                """
            ).fetchall()
        ]
        reconciliation_view_columns = [
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'vw_latest_reconciliation'
                ORDER BY ordinal_position
                """
            ).fetchall()
        ]
        data_quality_view_columns = [
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'vw_latest_data_quality'
                ORDER BY ordinal_position
                """
            ).fetchall()
        ]
        assert reconciliation_columns == RECONCILIATION_COLUMNS
        assert reconciliation_view_columns == RECONCILIATION_COLUMNS
        assert data_quality_view_columns == DATA_QUALITY_COLUMNS
        assert connection.execute(
            "SELECT COUNT(*) FROM control.vw_latest_reconciliation"
        ).fetchone()[0] >= 1
        assert connection.execute(
            "SELECT COUNT(*) FROM control.vw_latest_data_quality"
        ).fetchone()[0] >= 1
    finally:
        connection.close()


def test_legacy_reconciliation_view_is_rebound_after_schema_upgrade(
    tmp_path,
) -> None:
    database = tmp_path / "legacy_reconciliation_view.duckdb"
    connection = duckdb.connect(str(database))
    try:
        connection.execute("CREATE SCHEMA control")
        connection.execute(
            """
            CREATE TABLE control.reconciliation_result (
                reconciliation_id VARCHAR PRIMARY KEY,
                etl_batch_id VARCHAR NOT NULL,
                source_asset_id VARCHAR,
                reconciliation_name VARCHAR NOT NULL,
                source_value DOUBLE,
                warehouse_value DOUBLE,
                absolute_difference DOUBLE,
                tolerance DOUBLE NOT NULL,
                status VARCHAR NOT NULL,
                reconciled_at TIMESTAMP NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE control.data_quality_result (
                quality_result_id VARCHAR PRIMARY KEY,
                etl_batch_id VARCHAR NOT NULL,
                source_asset_id VARCHAR,
                check_name VARCHAR NOT NULL,
                check_scope VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                actual_value VARCHAR,
                expected_value VARCHAR,
                details VARCHAR,
                checked_at TIMESTAMP NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE VIEW control.vw_latest_reconciliation AS
            SELECT *
            FROM control.reconciliation_result
            """
        )
        connection.execute(
            """
            CREATE VIEW control.vw_latest_data_quality AS
            SELECT *
            FROM control.data_quality_result
            """
        )

        ensure_reconciliation_result_schema(connection)

        try:
            connection.execute(
                "SELECT COUNT(*) FROM control.vw_latest_reconciliation"
            ).fetchone()
        except duckdb.BinderException:
            pass
        else:
            raise AssertionError(
                "The legacy SELECT * view should be stale after table expansion."
            )

        refresh_control_views(connection)

        reconciliation_view_columns = [
            row[0]
            for row in connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'control'
                  AND table_name = 'vw_latest_reconciliation'
                ORDER BY ordinal_position
                """
            ).fetchall()
        ]
        assert reconciliation_view_columns == RECONCILIATION_COLUMNS
        assert connection.execute(
            "SELECT COUNT(*) FROM control.vw_latest_reconciliation"
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT COUNT(*) FROM control.vw_latest_data_quality"
        ).fetchone() == (0,)
    finally:
        connection.close()
