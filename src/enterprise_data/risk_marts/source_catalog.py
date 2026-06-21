from __future__ import annotations

from pathlib import Path

from src.enterprise_data.config import ROOT_DIR, WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse
from src.enterprise_data.risk_marts.contracts import ViewDefinition


PHASE4D_SQL_DIR = ROOT_DIR / "sql" / "phase4d"

VIEW_DEFINITIONS = (
    ViewDefinition(
        "vw_concentration_risk_current",
        PHASE4D_SQL_DIR / "001_concentration_risk_current.sql",
        ("mart.mart_credit_risk_current",),
    ),
    ViewDefinition(
        "vw_portfolio_quality_current",
        PHASE4D_SQL_DIR / "002_portfolio_quality_current.sql",
        ("mart.mart_credit_risk_current",),
    ),
    ViewDefinition(
        "vw_watchlist_intelligence_current",
        PHASE4D_SQL_DIR / "003_watchlist_intelligence_current.sql",
        ("mart.mart_credit_risk_current",),
    ),
    ViewDefinition(
        "vw_model_governance_current",
        PHASE4D_SQL_DIR / "004_model_governance_current.sql",
        (
            "core.dim_model",
            "core.dim_model_artifact",
            "core.fact_model_performance",
            "core.fact_model_validation",
        ),
    ),
    ViewDefinition(
        "vw_enterprise_risk_summary_current",
        PHASE4D_SQL_DIR / "005_enterprise_risk_summary_current.sql",
        (
            "mart.vw_portfolio_quality_current",
            "mart.vw_concentration_risk_current",
            "mart.vw_model_governance_current",
            "control.etl_batch",
            "control.etl_quality_summary",
            "control.reconciliation_result",
            "control.publish_status",
        ),
    ),
)

VIEW_NAMES = tuple(definition.view_name for definition in VIEW_DEFINITIONS)

EXISTING_MARTS = (
    "mart_credit_risk_current",
    "mart_ifrs9_stage_current",
    "mart_ews_current",
    "mart_model_risk",
    "mart_executive_current",
    "mart_data_quality",
)


def open_read_only(database_path: Path | str = WAREHOUSE_DB):
    return connect_warehouse(database_path, read_only=True)


def warehouse_inventory(connection) -> dict:
    schema_count = int(
        connection.execute(
            """
            SELECT COUNT(DISTINCT schema_name)
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'main', 'pg_catalog')
            """
        ).fetchone()[0]
    )
    table_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('information_schema', 'pg_catalog')
            """
        ).fetchone()[0]
    )
    view_count = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_type = 'VIEW'
              AND table_schema NOT IN ('information_schema', 'pg_catalog')
            """
        ).fetchone()[0]
    )
    return {
        "schema_count": schema_count,
        "table_count": table_count,
        "view_count": view_count,
    }


def existing_mart_row_counts(connection) -> dict[str, int]:
    return {
        table: int(
            connection.execute(
                f"SELECT COUNT(*) FROM mart.{table}"
            ).fetchone()[0]
        )
        for table in EXISTING_MARTS
    }


def phase4d_view_row_counts(connection) -> dict[str, int]:
    return {
        view: int(
            connection.execute(
                f"SELECT COUNT(*) FROM mart.{view}"
            ).fetchone()[0]
        )
        for view in VIEW_NAMES
    }


def latest_published_batch_id(connection) -> str:
    row = connection.execute(
        """
        SELECT batch.etl_batch_id
        FROM control.etl_batch batch
        JOIN control.publish_status publish
          ON publish.etl_batch_id = batch.etl_batch_id
        WHERE batch.batch_type = 'PHASE4B_CONTROL'
          AND batch.status = 'SUCCESS'
          AND publish.status = 'PUBLISHED'
        ORDER BY COALESCE(publish.transition_at, publish.published_at) DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("No published Phase 4B batch is available.")
    return str(row[0])


def source_context(connection) -> dict:
    source = connection.execute(
        """
        SELECT
            MIN(source_asset_id),
            MIN(source_run_id),
            MIN(source_model_version),
            COUNT(*)
        FROM mart.mart_credit_risk_current
        """
    ).fetchone()
    if source is None or source[0] is None:
        raise RuntimeError("Current credit-risk mart is unavailable.")
    source_asset_id = str(source[0])
    source_row = connection.execute(
        """
        SELECT sha256
        FROM control.source_asset
        WHERE source_asset_id = ?
        ORDER BY last_seen_at DESC
        LIMIT 1
        """,
        [source_asset_id],
    ).fetchone()
    if source_row is None:
        raise RuntimeError("Current scored-portfolio source hash is unresolved.")
    return {
        "source_asset_id": source_asset_id,
        "source_hash": str(source_row[0]),
        "source_run_id": str(source[1]),
        "model_version": str(source[2]),
        "portfolio_count": int(source[3]),
        "published_batch_id": latest_published_batch_id(connection),
    }
