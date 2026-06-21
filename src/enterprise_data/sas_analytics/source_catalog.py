from __future__ import annotations

from pathlib import Path

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse
from src.enterprise_data.sas_analytics.contracts import (
    AnalyticsContractError,
    AnalyticsRunMetadata,
    utc_timestamp,
)


PRIMARY_SOURCES = {
    "portfolio": "mart.mart_credit_risk_current",
    "ifrs9_stage": "mart.mart_ifrs9_stage_current",
    "ews": "mart.mart_ews_current",
    "model_risk": "mart.mart_model_risk",
    "executive": "mart.mart_executive_current",
    "data_quality": "mart.mart_data_quality",
}

SECONDARY_SOURCES = {
    "borrower": "core.dim_borrower",
    "facility": "core.dim_credit_facility",
    "model": "core.dim_model",
    "model_artifact": "core.dim_model_artifact",
    "model_performance": "core.fact_model_performance",
    "model_validation": "core.fact_model_validation",
    "feature_importance": "core.fact_feature_importance",
}

ALLOWLISTED_STAGING_SOURCES = {
    "calibration_deciles": "staging.stg_calibration_decile",
    "challenger_comparison": "staging.stg_challenger_comparison",
    "challenger_performance": "staging.stg_challenger_performance",
    "oot_summary": "staging.stg_oot_summary",
    "oot_risk_band_shift": "staging.stg_oot_risk_band_shift",
    "oot_score_shift": "staging.stg_oot_score_shift",
}

ALL_SOURCES = {
    **PRIMARY_SOURCES,
    **SECONDARY_SOURCES,
    **ALLOWLISTED_STAGING_SOURCES,
}


def open_read_only(database_path: Path | str = WAREHOUSE_DB):
    return connect_warehouse(database_path, read_only=True)


def source_object(source_name: str) -> str:
    try:
        return ALL_SOURCES[source_name]
    except KeyError as exc:
        raise AnalyticsContractError(
            f"Warehouse source is not allowlisted for Phase 4C: {source_name}"
        ) from exc


def table_frame(connection, source_name: str):
    return connection.execute(
        f"SELECT * FROM {source_object(source_name)}"
    ).fetchdf()


def _latest_published_batch(connection) -> str:
    row = connection.execute(
        """
        SELECT b.etl_batch_id
        FROM control.etl_batch b
        JOIN control.publish_status p
          ON p.etl_batch_id = b.etl_batch_id
        WHERE b.batch_type = 'PHASE4B_CONTROL'
          AND b.status = 'SUCCESS'
          AND p.status = 'PUBLISHED'
        ORDER BY COALESCE(p.transition_at, p.published_at) DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise AnalyticsContractError(
            "No successfully published Phase 4B batch is available."
        )
    return str(row[0])


def _validate_controls(connection, batch_id: str) -> None:
    quality = connection.execute(
        """
        SELECT quality_status
        FROM control.etl_quality_summary
        WHERE etl_batch_id = ?
        """,
        [batch_id],
    ).fetchone()
    if quality is None or quality[0] == "FAIL":
        raise AnalyticsContractError(
            f"Published batch {batch_id} does not have an acceptable DQ status."
        )
    failures = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM control.reconciliation_result
            WHERE etl_batch_id = ? AND status <> 'PASS'
            """,
            [batch_id],
        ).fetchone()[0]
    )
    if failures:
        raise AnalyticsContractError(
            f"Published batch {batch_id} has failed reconciliations."
        )


def run_metadata(connection) -> AnalyticsRunMetadata:
    batch_id = _latest_published_batch(connection)
    _validate_controls(connection, batch_id)
    source = connection.execute(
        """
        SELECT source_asset_id, sha256, row_count
        FROM control.source_asset
        WHERE relative_path = 'data/processed/scored_portfolio.csv'
        ORDER BY last_seen_at DESC
        LIMIT 1
        """
    ).fetchone()
    model = connection.execute(
        """
        SELECT source_model_version, COUNT(*)
        FROM mart.mart_credit_risk_current
        GROUP BY source_model_version
        """
    ).fetchall()
    if source is None or len(model) != 1:
        raise AnalyticsContractError(
            "Current portfolio source or model-version contract is unresolved."
        )
    portfolio_size = int(model[0][1])
    if portfolio_size != int(source[2]):
        raise AnalyticsContractError(
            "Published portfolio count does not match the registered source."
        )
    timestamp = utc_timestamp()
    run_id = (
        timestamp.replace("-", "").replace(":", "")
        .replace("T", "T").replace("Z", "Z")
        + "_"
        + str(source[1])[:8]
    )
    return AnalyticsRunMetadata(
        analytics_run_id=run_id,
        execution_timestamp=timestamp,
        source_asset_id=str(source[0]),
        source_hash=str(source[1]),
        published_batch_id=batch_id,
        model_version=str(model[0][0]),
        portfolio_size=portfolio_size,
    )


def warehouse_signature(connection) -> list[tuple]:
    rows = connection.execute(
        """
        SELECT
            t.table_schema,
            t.table_name,
            t.table_type,
            COUNT(c.column_name) AS column_count
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c
          ON c.table_schema = t.table_schema
         AND c.table_name = t.table_name
        WHERE t.table_schema IN ('control', 'staging', 'reference', 'core', 'mart')
        GROUP BY t.table_schema, t.table_name, t.table_type
        ORDER BY t.table_schema, t.table_name
        """
    ).fetchall()
    return [tuple(row) for row in rows]


def warehouse_row_counts(connection) -> dict[str, int]:
    objects = connection.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('control', 'staging', 'reference', 'core', 'mart')
          AND table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name
        """
    ).fetchall()
    return {
        f"{schema}.{table}": int(
            connection.execute(
                f'SELECT COUNT(*) FROM {schema}."{table}"'
            ).fetchone()[0]
        )
        for schema, table in objects
    }
