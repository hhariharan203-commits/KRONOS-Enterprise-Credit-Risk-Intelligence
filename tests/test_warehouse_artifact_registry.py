from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse


def test_artifacts_are_registered_without_binary_contents() -> None:
    connection = connect_warehouse(WAREHOUSE_DB, read_only=True)
    try:
        artifact_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.artifact_registry
            WHERE is_current
            """
        ).fetchone()[0]
        assert artifact_count >= 53

        binary_count, stored_binary_count = connection.execute(
            """
            SELECT
                COUNT(*),
                SUM(CASE WHEN binary_stored THEN 1 ELSE 0 END)
            FROM control.artifact_registry
            WHERE content_class = 'BINARY_METADATA_ONLY'
              AND is_current
            """
        ).fetchone()
        assert binary_count > 0
        assert stored_binary_count == 0

        registered = {
            row[0]
            for row in connection.execute(
                """
                SELECT relative_path
                FROM control.artifact_registry
                WHERE is_current
                """
            ).fetchall()
        }
        assert {
            "models/pd_model.pkl",
            "models/lgd_model.pkl",
            "models/ead_model.pkl",
            "reports/model_validation_pack.pdf",
            "sql/phase4d/001_concentration_risk_current.sql",
            "sql/phase4d/002_portfolio_quality_current.sql",
            "sql/phase4d/003_watchlist_intelligence_current.sql",
            "sql/phase4d/004_model_governance_current.sql",
            "sql/phase4d/005_enterprise_risk_summary_current.sql",
            "sql/phase4d/rollback_phase4d_views.sql",
        }.issubset(registered)
    finally:
        connection.close()
