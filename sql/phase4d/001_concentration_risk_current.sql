CREATE OR REPLACE VIEW mart.vw_concentration_risk_current AS
WITH grouped AS (
    SELECT
        'INDUSTRY' AS dimension_type,
        COALESCE(industry, 'UNKNOWN') AS category,
        COUNT(*) AS account_count,
        SUM(ead) AS total_ead,
        AVG(pd_score) AS average_pd,
        AVG(lgd) AS average_lgd,
        SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
        SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
        SUM(pd_score * lgd * ead) AS current_credit_loss_proxy,
        MIN(source_run_id) AS source_run_id,
        MIN(source_model_version) AS source_model_version,
        MAX(warehouse_loaded_at) AS warehouse_snapshot_timestamp
    FROM mart.mart_credit_risk_current
    GROUP BY COALESCE(industry, 'UNKNOWN')

    UNION ALL

    SELECT
        'REGION',
        COALESCE(region, 'UNKNOWN'),
        COUNT(*),
        SUM(ead),
        AVG(pd_score),
        AVG(lgd),
        SUM(pd_score * ead) / NULLIF(SUM(ead), 0),
        SUM(lgd * ead) / NULLIF(SUM(ead), 0),
        SUM(pd_score * lgd * ead),
        MIN(source_run_id),
        MIN(source_model_version),
        MAX(warehouse_loaded_at)
    FROM mart.mart_credit_risk_current
    GROUP BY COALESCE(region, 'UNKNOWN')

    UNION ALL

    SELECT
        'RISK_BAND',
        COALESCE(risk_band, 'UNKNOWN'),
        COUNT(*),
        SUM(ead),
        AVG(pd_score),
        AVG(lgd),
        SUM(pd_score * ead) / NULLIF(SUM(ead), 0),
        SUM(lgd * ead) / NULLIF(SUM(ead), 0),
        SUM(pd_score * lgd * ead),
        MIN(source_run_id),
        MIN(source_model_version),
        MAX(warehouse_loaded_at)
    FROM mart.mart_credit_risk_current
    GROUP BY COALESCE(risk_band, 'UNKNOWN')

    UNION ALL

    SELECT
        'RISK_GRADE',
        COALESCE(risk_grade, 'UNKNOWN'),
        COUNT(*),
        SUM(ead),
        AVG(pd_score),
        AVG(lgd),
        SUM(pd_score * ead) / NULLIF(SUM(ead), 0),
        SUM(lgd * ead) / NULLIF(SUM(ead), 0),
        SUM(pd_score * lgd * ead),
        MIN(source_run_id),
        MIN(source_model_version),
        MAX(warehouse_loaded_at)
    FROM mart.mart_credit_risk_current
    GROUP BY COALESCE(risk_grade, 'UNKNOWN')
),
shares AS (
    SELECT
        *,
        total_ead / NULLIF(
            SUM(total_ead) OVER (PARTITION BY dimension_type),
            0
        ) AS exposure_share
    FROM grouped
),
concentration AS (
    SELECT
        *,
        POWER(exposure_share, 2) AS hhi_contribution
    FROM shares
)
SELECT
    dimension_type,
    category,
    account_count,
    total_ead,
    exposure_share,
    hhi_contribution,
    SUM(hhi_contribution) OVER (PARTITION BY dimension_type) AS hhi,
    average_pd,
    average_lgd,
    weighted_pd,
    weighted_lgd,
    current_credit_loss_proxy,
    source_run_id,
    source_model_version,
    warehouse_snapshot_timestamp
FROM concentration;
