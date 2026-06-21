CREATE OR REPLACE VIEW mart.vw_model_governance_current AS
WITH model_families AS (
    SELECT * FROM (VALUES ('PD'), ('LGD'), ('EAD')) AS families(model_family)
),
performance AS (
    SELECT
        model_family,
        MAX(CASE WHEN metric_name = 'roc_auc'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS roc_auc,
        MAX(CASE WHEN metric_name = 'accuracy'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS accuracy,
        MAX(CASE WHEN metric_name = 'precision'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS precision,
        MAX(CASE WHEN metric_name = 'recall'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS recall,
        MAX(CASE WHEN metric_name = 'f1_score'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS f1_score,
        MAX(CASE WHEN metric_name = 'mae'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS mae,
        MAX(CASE WHEN metric_name = 'rmse'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS rmse,
        MAX(CASE WHEN metric_name = 'r2_score'
                 THEN TRY_CAST(metric_value AS DOUBLE) END) AS r2_score,
        MAX(CASE WHEN metric_name = 'feature_count'
                 THEN TRY_CAST(metric_value AS BIGINT) END) AS feature_count,
        MAX(CASE WHEN metric_name = 'train_samples'
                 THEN TRY_CAST(metric_value AS BIGINT) END) AS train_samples,
        MAX(CASE WHEN metric_name = 'test_samples'
                 THEN TRY_CAST(metric_value AS BIGINT) END) AS test_samples
    FROM core.fact_model_performance
    GROUP BY model_family
),
validation_pack AS (
    SELECT metrics_json, validation_status
    FROM core.fact_model_validation
    WHERE validation_type =
        'outputs/model_validation_pack/validation_summary.json'
    LIMIT 1
),
calibration AS (
    SELECT metrics_json
    FROM core.fact_model_validation
    WHERE validation_type = 'outputs/calibration/calibration_summary.json'
    LIMIT 1
),
governance AS (
    SELECT metrics_json
    FROM core.fact_model_validation
    WHERE validation_type =
        'outputs/model_validation_pack/governance_summary.json'
    LIMIT 1
),
challenger AS (
    SELECT metrics_json
    FROM core.fact_model_validation
    WHERE validation_type =
        'outputs/challenger_models/challenger_summary.json'
    LIMIT 1
),
psi AS (
    SELECT metrics_json
    FROM core.fact_model_validation
    WHERE validation_type = 'outputs/oot_validation/psi_report.json'
    LIMIT 1
),
artifact_counts AS (
    SELECT model_family, COUNT(*) AS artifact_count
    FROM core.dim_model_artifact
    GROUP BY model_family
),
model_context AS (
    SELECT
        MIN(model_version) AS model_version,
        MIN(artifact_match_status) AS artifact_match_status
    FROM core.dim_model
)
SELECT
    families.model_family,
    model_context.model_version,
    model_context.artifact_match_status,
    COALESCE(artifact_counts.artifact_count, 0) AS artifact_count,
    CASE
        WHEN families.model_family = 'PD'
            THEN COALESCE(
                JSON_EXTRACT_STRING(
                    validation_pack.metrics_json,
                    '$.approval_status'
                ),
                validation_pack.validation_status
            )
        ELSE 'NOT INDEPENDENTLY VALIDATED'
    END AS approval_status,
    CASE
        WHEN families.model_family = 'PD'
            THEN COALESCE(
                JSON_EXTRACT_STRING(
                    validation_pack.metrics_json,
                    '$.calibration_status'
                ),
                'NOT AVAILABLE'
            )
        ELSE 'NOT APPLICABLE'
    END AS calibration_status,
    CASE
        WHEN families.model_family = 'PD'
            THEN TRY_CAST(
                JSON_EXTRACT_STRING(psi.metrics_json, '$.psi')
                AS DOUBLE
            )
        ELSE NULL
    END AS psi,
    CASE
        WHEN families.model_family = 'PD'
            THEN COALESCE(
                JSON_EXTRACT_STRING(
                    challenger.metrics_json,
                    '$.model_replacement'
                ),
                'NOT AVAILABLE'
            )
        ELSE 'NOT AVAILABLE'
    END AS challenger_status,
    CASE
        WHEN families.model_family = 'PD'
            THEN COALESCE(
                validation_pack.validation_status,
                'NOT AVAILABLE'
            )
        ELSE 'NOT AVAILABLE'
    END AS validation_status,
    COALESCE(
        CASE families.model_family
            WHEN 'PD' THEN JSON_EXTRACT_STRING(
                governance.metrics_json,
                '$.model_governance_results.PD.status'
            )
            WHEN 'LGD' THEN JSON_EXTRACT_STRING(
                governance.metrics_json,
                '$.model_governance_results.LGD.status'
            )
            WHEN 'EAD' THEN JSON_EXTRACT_STRING(
                governance.metrics_json,
                '$.model_governance_results.EAD.status'
            )
        END,
        'NOT AVAILABLE'
    ) AS governance_status,
    performance.roc_auc,
    performance.accuracy,
    performance.precision,
    performance.recall,
    performance.f1_score,
    CASE
        WHEN families.model_family = 'PD'
            THEN TRY_CAST(
                JSON_EXTRACT_STRING(
                    calibration.metrics_json,
                    '$.brier_score'
                )
                AS DOUBLE
            )
        ELSE NULL
    END AS brier_score,
    performance.mae,
    performance.rmse,
    performance.r2_score,
    performance.feature_count,
    performance.train_samples,
    performance.test_samples,
    CASE
        WHEN families.model_family = 'PD'
            THEN JSON_EXTRACT_STRING(
                validation_pack.metrics_json,
                '$.champion_model'
            )
        ELSE NULL
    END AS champion_model,
    CASE
        WHEN families.model_family = 'PD'
            THEN JSON_EXTRACT_STRING(
                challenger.metrics_json,
                '$.best_challenger'
            )
        ELSE NULL
    END AS best_challenger,
    CASE
        WHEN families.model_family = 'PD'
            THEN TRY_CAST(
                JSON_EXTRACT_STRING(
                    challenger.metrics_json,
                    '$.performance_gap_best_challenger_minus_champion_auc'
                )
                AS DOUBLE
            )
        ELSE NULL
    END AS challenger_auc_gap
FROM model_families families
LEFT JOIN performance
  ON performance.model_family = families.model_family
LEFT JOIN artifact_counts
  ON artifact_counts.model_family = families.model_family
CROSS JOIN model_context
CROSS JOIN validation_pack
CROSS JOIN calibration
CROSS JOIN governance
CROSS JOIN challenger
CROSS JOIN psi;
