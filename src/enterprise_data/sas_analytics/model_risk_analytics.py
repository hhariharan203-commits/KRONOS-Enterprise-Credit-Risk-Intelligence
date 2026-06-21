from __future__ import annotations

import json

import pandas as pd

from src.enterprise_data.sas_analytics.source_catalog import table_frame


def _typed_performance(connection) -> pd.DataFrame:
    frame = table_frame(connection, "model_performance")[
        ["model_family", "metric_name", "metric_value", "source_generated_at"]
    ].copy()
    numeric_values = []
    text_values = []
    for value in frame["metric_value"]:
        try:
            parsed = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            parsed = value
        if isinstance(parsed, (int, float)) and not isinstance(parsed, bool):
            numeric_values.append(float(parsed))
            text_values.append(None)
        else:
            numeric_values.append(None)
            text_values.append(None if parsed is None else str(parsed))
    frame["numeric_value"] = numeric_values
    frame["text_value"] = text_values
    return frame


def model_inventory(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            model.model_version,
            model.model_version_source,
            model.artifact_match_status,
            model.notes,
            COUNT(artifact.artifact_id) AS artifact_count,
            COUNT(DISTINCT artifact.model_family) AS model_family_count
        FROM core.dim_model model
        CROSS JOIN core.dim_model_artifact artifact
        GROUP BY
            model.model_version,
            model.model_version_source,
            model.artifact_match_status,
            model.notes
        """
    ).fetchdf()


def model_artifact_inventory(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            model_family,
            artifact_role,
            COUNT(*) AS artifact_count,
            SUM(size_bytes) AS total_size_bytes
        FROM core.dim_model_artifact
        GROUP BY model_family, artifact_role
        ORDER BY model_family, artifact_role
        """
    ).fetchdf()


def validation_summary(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            validation_type,
            COALESCE(validation_status, 'NOT EXPLICITLY STATED')
                AS validation_status,
            source_generated_at,
            warehouse_loaded_at
        FROM core.fact_model_validation
        ORDER BY validation_type
        """
    ).fetchdf()


def governance_summary(connection) -> pd.DataFrame:
    return connection.execute(
        """
        WITH latest_batch AS (
            SELECT etl_batch_id
            FROM control.etl_batch
            WHERE batch_type = 'PHASE4B_CONTROL' AND status = 'SUCCESS'
            ORDER BY completed_at DESC
            LIMIT 1
        ),
        quality AS (
            SELECT quality_score, quality_status
            FROM control.etl_quality_summary
            WHERE etl_batch_id = (SELECT etl_batch_id FROM latest_batch)
        ),
        reconciliation AS (
            SELECT
                COUNT(*) AS reconciliation_count,
                SUM(CASE WHEN status <> 'PASS' THEN 1 ELSE 0 END)
                    AS reconciliation_failures
            FROM control.reconciliation_result
            WHERE etl_batch_id = (SELECT etl_batch_id FROM latest_batch)
        )
        SELECT
            (SELECT etl_batch_id FROM latest_batch) AS published_batch_id,
            quality.quality_score,
            quality.quality_status,
            reconciliation.reconciliation_count,
            reconciliation.reconciliation_failures,
            (SELECT COUNT(*) FROM core.fact_model_performance)
                AS performance_metric_count,
            (SELECT COUNT(*) FROM core.fact_model_validation)
                AS validation_record_count,
            (SELECT COUNT(*) FROM core.fact_feature_importance)
                AS feature_importance_count
        FROM quality
        CROSS JOIN reconciliation
        """
    ).fetchdf()


def psi_summary(connection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            SUM(psi_contribution) AS population_stability_index,
            MAX(ABS(pct_point_shift)) AS maximum_percentage_point_shift,
            COUNT(*) AS score_bucket_count
        FROM staging.stg_oot_score_shift
        """
    ).fetchdf()


def run_model_risk_analytics(connection) -> dict[str, pd.DataFrame]:
    return {
        "model_inventory": model_inventory(connection),
        "model_artifact_inventory": model_artifact_inventory(connection),
        "model_performance_summary": _typed_performance(connection),
        "model_validation_summary": validation_summary(connection),
        "model_governance_summary": governance_summary(connection),
        "calibration_deciles": table_frame(connection, "calibration_deciles"),
        "challenger_comparison": table_frame(
            connection,
            "challenger_comparison",
        ),
        "challenger_performance": table_frame(
            connection,
            "challenger_performance",
        ),
        "oot_summary": table_frame(connection, "oot_summary"),
        "oot_risk_band_shift": table_frame(
            connection,
            "oot_risk_band_shift",
        ),
        "oot_score_shift": table_frame(connection, "oot_score_shift"),
        "psi_summary": psi_summary(connection),
    }
